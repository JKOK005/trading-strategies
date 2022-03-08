## Arbitrag Bot scanner

### Example of execution
```python
python3 ./main/general/scanner/arbitrag_scanner.py \
--exchange okx \
--asset_type spot-perp \
--db_url xxx \
--message_url xxx \
--message_port xxx \
--processors 4 \
--samples 120
```

Flag / description pairs are explained below.

| Flag | Description | Example |
| --- | --- | --- |
| exchange | Exchange for trading currency pair | kucoin |
| asset_type | Asset pair traded | spot-perp |
| db_url | URL pointing to database | - |
| message_url | URL pointing to queuing system (possibly Redis) | - |
| message_port | Port pointing to queuing system (possible Redis) | - |
| processors | CPU cores for parallelizing query to exchange | 4 |
| samples | Number of 1 second intervals at which prirce and funding rates are sampled. We will take the average score across all samples. | 120 |

### Tips on running docker file
In the event that the script encounters the error:

```
urllib3.exceptions.ProtocolError: ('Connection aborted.', FileNotFoundError(2, 'No such file or directory'))
```

The solution would be to add a mount point to the docker file:

```
docker run -v /var/run/docker.sock:/var/run/docker.sock
```

Reference taken from [here](https://forums.docker.com/t/docker-sdk-for-python/96330/2)