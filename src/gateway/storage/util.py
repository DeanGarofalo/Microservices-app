import pika, json

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)
    except Exception as err:
        return "Internal Server Error", 500
    
    message = {
        "video_fid": str(fid),
        "mp4_fid": None,
        "username": access["username"],
    }
    try:
        channel.basic_publish(
            exchange="", 
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(deliver_mode=pika.spec.PERSISTENT_DELIVERY_MODE)
        )
    except:
        fs.delete(fid)
        return "Internal Server Error", 500