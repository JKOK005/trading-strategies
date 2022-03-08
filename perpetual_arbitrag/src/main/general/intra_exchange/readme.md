## Arbitrag Bot manager--poll_interval_s 3600 \


### Example of execution
```python
python3 ./main/general/intra_exchange/arbitrag_manager.py \
--user_id 1 \
--exchange okx \
--asset_type spot-perp \
--jobs 3 \
--db_url xxx \
--message_url xxx \
--message_port xxx
```

Flag / description pairs are explained below.

| Flag | Description | Example |
| --- | --- | --- |
| user_id | User assigned ID | 1 |
| exchange | Exchange for trading currency pair | kucoin |
| asset_type | Asset pair traded | spot-perp |
| jobs | Maximum jobs allowed to be run | 1 |
| db_url | URL pointing to database | - |
| message_url | URL pointing to queuing system (possibly Redis) | - |
| message_port | Port pointing to queuing system (possible Redis) | - |

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