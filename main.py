from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import sqlite3
import string 
import os
from web3 import Web3

DB_FILE = os.getenv("DB_FILE", "preimages.db")
DECODED_DATA_FILE = os.getenv("DECODED_DATA_FILE", "decoded_data")

app = FastAPI()
origins = [
    "http://localhost",
    "http://127.0.0.1"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def write_to_db(f, conn):
    c = conn.cursor()
    # skip first 6 lines, geth export info
    for _ in range(6):
        f.readline()

    while True:
        f.readline()
        hash_line = f.readline()
        preimage_line = f.readline()
        if not hash_line or not preimage_line:
            break
        hash = hash_line.strip()[22:]
        preimage = preimage_line.strip()
        c.execute("INSERT INTO hash_preimage VALUES (?, ?)", (hash, preimage))
    conn.commit()


def create_db():
   # subprocess.run(["./rlpdump", "./preimages.rlp > decoded_data"])
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS hash_preimage
                 (hash text, preimage text)''')
    c.execute("CREATE INDEX IF NOT EXISTS hash_index ON hash_preimage (hash)")
    with open(DECODED_DATA_FILE, "r") as f:
        write_to_db(f, conn)
    conn.close()

def search_db(input_string):
    c = conn.cursor()
    c.execute("SELECT preimage FROM hash_preimage WHERE hash=?", (input_string,))
    result = c.fetchone()
    print(result, input_string)
    if result: 
        return result[0], "preimage"
    else:
        h=Web3.keccak(hexstr=input_string).hex()[2:]
        c.execute("SELECT preimage FROM hash_preimage WHERE hash=?", (h,))
        result = c.fetchone()
        if result:
            return h, "hash"
        else:
            return None, "Not found"

def get_db_conn():
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

@app.post("/")
async def search(input: str):
    input_string = input[2:] if input.startswith('0x') else input
    if not all(c in string.hexdigits for c in input_string) or (len(input_string) > 64) or (len(input_string) < 40):
        return {"error": "Invalid input"}
    else:
        result, status = search_db(input_string)
        if result:
            # result is preimage
            if status == "preimage":
                h=Web3.keccak(hexstr=input_string).hex()[2:]
                return {"key": input_string, "preimage": result, "hash": h}
            # result is hash
            elif status == "hash":
                h=Web3.keccak(hexstr=result).hex()[2:]
                return {"key": result, "preimage": input_string, "hash": h}
            # not found
            else:
                return {"error": status} 
        else:
            return {"error": status} 


if not os.path.exists(DB_FILE):
    create_db()
    conn = sqlite3.connect(DB_FILE)
else:
    conn = sqlite3.connect(DB_FILE)
