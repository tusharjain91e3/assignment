import UserModel from '@/models/User';
import { getServerSession } from 'next-auth/next';
import sequelize from '@/models/db';
import { User } from 'next-auth';
import Message from '@/models/Message';
import { NextRequest } from 'next/server';
import { authOptions } from '../../auth/[...nextauth]/options';

export async function DELETE(
  request: Request,
  { params }: { params: { messageid: string } }
) {
  const messageId = params.messageid;
  await sequelize.authenticate();
  const session = await getServerSession(authOptions);
  const _user: User = session?.user;
  if (!session || !_user) {
    return Response.json(
      { success: false, message: 'Not authenticated' },
      { status: 401 }
    );
  }

  try {
    // Find the user by id
    const userInstance = await UserModel.findOne({ where: { id: _user._id } });
    if (!userInstance) {
      return Response.json(
        { message: 'User not found', success: false },
        { status: 404 }
      );
    }
    // Get the current messages array (assuming it's a JSON/array field)
    // @ts-ignore
    // Fix: Ensure messages is always an array and has array methods
    let messages: any[] = Array.isArray(userInstance.get('messages')) ? userInstance.get('messages') : [];
    const originalLength = messages.length;
    messages = messages.filter((msg: any) => {
      // Support both string and object id
      if (typeof msg === 'string') return msg !== messageId;
      if (msg && (msg.id || msg._id)) {
        return msg.id !== messageId && msg._id !== messageId;
      }
      return true;
    });

    // Only update if something was actually removed
    if (messages.length === originalLength) {
      return Response.json(
        { message: 'Message not found or already deleted', success: false },
        { status: 404 }
      );
    }

    // Instead of updating a non-existent 'messages' property on user,
    // delete the message directly from the Message table, ensuring the message belongs to the user.
    const deleteCount = await Message.destroy({
      where: {
        id: messageId,
        userId: userInstance.id,
      },
    });

    if (deleteCount === 0) {
      return Response.json(
        { message: 'Message not found or already deleted', success: false },
        { status: 404 }
      );
    }

    return Response.json(
      { message: 'Message deleted', success: true },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error deleting message:', error);
    return Response.json(
      { message: 'Error deleting message', success: false },
      { status: 500 }
    );
  }
}