from fastapi import FastAPI
import subprocess
import sqlite3
import hashlib
import string 
import os

app = FastAPI()

def decode(data):
    rows = []
    for i in range(6, len(data), 3):
        if i + 2 < len(data):
            hash = data[i+2].strip()
            preimage = data[i + 1].strip()[22:]
            rows.append((preimage, hash))
    return rows

def write_to_db(rows):
    conn = sqlite3.connect('preimages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS hash_preimage
                 (hash text, preimage text)''')
    c.execute("CREATE INDEX IF NOT EXISTS hash_index ON hash_preimage (hash)")
    c.executemany("INSERT INTO hash_preimage VALUES (?,?)", rows)
    conn.commit()
    conn.close()

def create_db():
    result = subprocess.run(["./rlpdump", "./preimages.rlp"], stdout=subprocess.PIPE)
    data = result.stdout.decode("utf-8").strip().split("\n")
    rows = decode(data)
    write_to_db(rows)


def search_db(input_string):
    c = conn.cursor()
    c.execute("SELECT preimage FROM hash_preimage WHERE hash=?", (input_string,))
    result = c.fetchone()
    if result:
        return result[0]
    else:
        c.execute("SELECT hash FROM hash_preimage WHERE preimage=?", (input_string,))
        result = c.fetchone()
        return result[0] if result else "Not found"

## Very slow, don't use for a big db 
def update_db():
    result = subprocess.run(["./rlpdump", "./preimages.rlp"], stdout=subprocess.PIPE)
    data = result.stdout.decode("utf-8").strip().split("\n")
    rows = decode(data)
    conn = sqlite3.connect('preimages.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS hash_preimage
                 (hash text, preimage text)''')
    for row in rows:
        c.execute("SELECT hash FROM hash_preimage WHERE preimage=?", (row[0],))
        result = c.fetchone()
        if not result:
            c.execute("INSERT INTO hash_preimage VALUES (?,?)", row)
    conn.commit()

def keccak_hex(hex_string):
    hex_bytes = bytes.fromhex(hex_string)
    return hashlib.sha3_256(hex_bytes).hexdigest()


@app.post("/search")
async def search(input: str):
    if len(input) > 64 or not all(c in string.hexdigits for c in input):
        return {"error": "Invalid input."}
    result = search_db(input)
    return {"result": result}

if __name__ == "__main__":
    create_db()

if os.path.exists("./preimages.db"):
    conn = sqlite3.connect("preimages.db")
else:
    create_db()
    conn = sqlite3.connect("preimages.db")
