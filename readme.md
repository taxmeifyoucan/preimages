# Geth preimages db

Tool for serving [Geth preimages](https://geth.ethereum.org/docs/faq#what-is-a-preimage) as a public database. It returns preimage of a key hash and vice versa. 

You can try it at https://preimages.bordel.wtf or by using the API:  
```
curl -X POST "https://preimages.bordel.wtf/search?input=0d2795d4a2e0305f62f46ece58c15a6fa1673779a6a3622640983d644c17625d"
{"result":"e83e0b36bc68c1407b81b6d42ca4bd23fc309517"}
```

## Usage

To run it locally, you will need golang and python. 

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
```. 

Now you can run the API using uvicorn. It's available at localhost:8000. 

```
uvicorn main:app --reload
```

