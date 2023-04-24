## connection detail

| direction | type | data       | meaning                                                                                                     |
|-----------|------|------------|-------------------------------------------------------------------------------------------------------------|
| C -> S    | JOIN |            | request space in lobby                                                                                      |
| S -> C    | CONT | bytes[1]   | you have been given a place in the lobby, follow with information. if data[1] is 0x01 server has a password |
|           | SALT | bytes[32]  | salt to use with the password                                                                               | 
| C -> S    | NAME | string[16] | your username (16 chars)                                                                                    |
|           | PSWD | bytes[32]  | servers password (sha256 hashed and salted)                                                                 |
|           | JOIN |            | join lobby, am now waiting                                                                                  |
| S -> C    | WAIT |            | waiting for game to start                                                                                   |

client is now waiting on the server.

## from this point on every 10s heartbeat is sent

| direction | type  | data | meaning            |
|-----------|-------|------|--------------------|
| C -> S    | HART  |      | heartbeat sent     |
| S -> C    | HART  |      | heartbeat received |


## game start

| direction | type  | data | meaning                                 |
|-----------|-------|------|-----------------------------------------|
| S -> C    | STRT  |      | game is starting please sync clocks     |
| C -> S    | TMPK  |      | request servers time                    |
| S -> C    | TMPK  |      | servers time (client uses ping to sync) |
| C -> S    | WAIT  |      | time synced, waiting                    | 

client waits for servers begin message

| direction | type  | data        | meaning                  |
|-----------|-------|-------------|--------------------------|
| S -> C    | BEGN  | int[4]      | start time               |
|           | FRST  | string[128] | start point of the game  |
|           | LAST  | string[128] | end point of the game    |


## when a client wins
| direction | type  | data        | meaning                            |
|-----------|-------|-------------|------------------------------------|
| C -> S    | IWIN  |             | I have reached the end goal        |
|           | PATH  | int[1]      | path length                        |
|           |       | string[128] | Path entry * for each item in path |
| S -> C    | CONG  |             | Congratulations you win!           |
client is assumed to be kicked from the server


## when a client looses
| direction | type  | data        | meaning                            |
|-----------|-------|-------------|------------------------------------|
| S -> C    | LOSE  |             | you have lost, path to follow      |
|           | PATH  | int[1]      | path length                        |
|           |       | string[128] | Path entry * for each item in path |
client is assumed to be kicked from the server 