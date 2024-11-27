from sqlalchemy import event, func
from app.models import Message, Thread


def register_message_events():
    @event.listens_for(Message, 'before_insert')
    def update_thread_updated_at(mapper, connection, target):
        print("Message event running")
        thread_id = target.thread_id
        if thread_id:
            connection.execute(
                Thread.__table__.update()
                .where(Thread.id == thread_id)
                .values(updated_at=func.now())
            )
