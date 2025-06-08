import UserModel from '@/models/User';
import sequelize from '@/models/db';
import Message from '@/models/Message';

export async function POST(request: Request) {
  await sequelize.authenticate();
  const { username, content } = await request.json();

  try {
    const user = await UserModel.findOne({ where: { username } });

    if (!user) {
      return Response.json(
        { message: 'User not found', success: false },
        { status: 404 }
      );
    }

    // Check if the user is accepting messages
    if (!user.isAcceptingMessaging) {
      return Response.json(
        { message: 'User is not accepting messages', success: false },
        { status: 403 } // 403 Forbidden status
      );
    }

    const newMessage = { content, createdAt: new Date() };

    // Create and associate the new message with the user
    await Message.create({
      content: newMessage.content,
      createdAt: newMessage.createdAt,
      userId: user.id,
    });

    return Response.json(
      { message: 'Message sent successfully', success: true },
      { status: 201 }
    );
  } catch (error) {
    console.error('Error adding message:', error);
    return Response.json(
      { message: 'Internal server error', success: false },
      { status: 500 }
    );
  }
}