# Geth preimages db

Tool for serving [Geth preimages](https://geth.ethereum.org/docs/faq#what-is-a-preimage) as a public database. It returns preimage of hash and vice versa. 

You can try it at https://preimages.bordel.wtf: 
```
curl -X POST "https://preimages.bordel.wtf/search?input=02d0be48221fdd04e71b6553dd686384fdd30db03b6ba03b2395c2bc5346771d"
{"result":"50660ad60b49f1cc39f6912d65dc6685919dae4e"}
```

## Usage

First, you need to export preimages from geth. This requires a geth node, ideally with `--cache.preimages` option allowed. Shut down the node and use `db` subcommand for export: 

```
geth db export preimage preimages.rlp
```
Exported data is RLP encoded and to work with it, you need `rlpdump` tool which comes with geth. Clone the [geth repo](https://github.com/ethereum/go-ethereum/, compile `rlpdump` and copy the binary to directory with this tool. 

```
cd go-ethereum/cmd/rlpdump
go build
cp rlpdump ~/preimages
```

Make sure you have python3 and install rest of dependencies:

```
cd preimages
pip3 install -r requirements.txt
```

Now you can run the API using `uvicorn`. First it will create sqlite database from the rlp data and then becomes available at localhost:8000. Note that database can reach around 2GB. 

```
uvicorn main:app --reload
```

