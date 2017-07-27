def notify_messages():
        messages = len(Message.query.filter(Message.recipient==g.user.handle).filter(Message.read==False).all()) or ""
	return str(messages)
