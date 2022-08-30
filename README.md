# baby_channel
## Summary
LINE bot for RaspberryPi.

### Function
#### 写真撮影（take photo）
If you send the message "写真撮影" to LINE bot, take a photo and post it to the talk.

#### 温湿度計測（Temperature and humidity measurement）
When "写真撮影", Notifies the current temperature and humidity after 写真撮影.

#### 認証（Authorization）　Unimplemented
When new User Follow this bot, ask to admin want to be approve.

```mermaid
sequenceDiagram
    autonumber
    actor User
    actor Admin
    participant Server as Server
    participant DB as DB

    User ->> Server: Some Request
    Server ->> DB: check users
    DB -->> Server: result
alt User is authenticated
    Note right of User: Do Action!

else User is not authenticated
    Server->>User: Message
    Note left of Server: "You are not authorized user,<br>Will you send auth request to admin?"<br>"あなたは未認証のユーザです。<br>adminに認証リクエストを送信しますか？"
    User-->>Server: Answer
    alt User's answer is "No"
        Server->>User: Message
        Note left of Server: "OK! good bye!"<br>"ほなさいなら"
    else　User's answer is "Yes"
        Server->>Admin: Message
        Note right of Admin: "Auth Request From "User", Will you Authenticate "User"?"<br>"○○から認証リクエストきたけど認証しちゃう？"
        Admin-->>Server:the Answer
            alt Admin's Answer is "No"
                Server-->>User: Message
                    Note right of User: "Sorry, You are denied from Admin"<br>"ごめん。あかんってさ"
            else  Admin's Answer is "Yes"
                Server->>DB:Save userId to Authenticated User
                DB-->>Server:Result
                Server-->>User: Message
                    Note right of User: "Congratulations, You are authenticated!"<br>"よかったね。承認されたみたいよ。"
            end
    end
end
```

## Install

- install SqLite
  - see [this Article](https://nekonisi.com/install_sqlite/)
  - or execute below command(Debian系)
  ```bash
  sudo apt install sqlite3 -y
  ```

- expand submodule

```
cd nekonisi_dht11;
git submodule update -i;
```
- install pip library
```
pip install -r requirements.txt
```

```
export LINE_CHANNEL_SECRET="{LINE_CHANNEL_SECRET}"
export LINE_CHANNEL_ACCESS_TOKEN="{LINE_CHANNEL_ACCESS_TOKEN}"
export LINE_ADMIN_USER_ID="{LINE_ADMIN_USER_ID}"
```

## execute

```
python app.php
```