from qiniu import Auth, put_data

access_key = "myY9NV3toBgSKjOOmu6qjYnyxyg-4TvXtYLyMp4B"
secret_key = "wem6iIhrkHcTBUHmCzWq3apj_uQPTO5l-qk3OPfK"
bucket_name = "enzyme"

def storage(data):
    try:
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = put_data(token, None, data)
    except Exception as e:
        raise e

    if info.status_code != 200:
        raise Exception("上传图片失败")

    return ret["key"]


    print(ret, info)

if __name__ == '__main__':
    file = input("请输入文件路径")
    with open(file, 'rb') as f:
        storage(f.read())