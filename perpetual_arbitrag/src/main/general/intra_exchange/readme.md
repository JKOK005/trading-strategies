## Arbitrag Bot manager

### Example of execution
```python
python3 main/intra_exchange/manager/arbitrag_manager.py \
--user_id 1 \
--db_url xxx \
--poll_interval_s 3600
```

Flag / description pairs are explained below.

| Flag | Description | Example |
| --- | --- | --- |
| user_id | User assigned ID | 1 |
| db_url | URL pointing to database | - |
| poll_interval_s | Checks evern N seconds to create new jobs or close existing ones | 3600 |

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