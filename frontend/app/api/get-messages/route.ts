import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth/next';
import { authOptions } from '../auth/[...nextauth]/options';
import sequelize from '@/models/db';
import UserModel from '@/models/User';
import { User } from 'next-auth';

export async function GET(request: NextRequest) {
  try {
    await sequelize.authenticate();

    const session = await getServerSession(authOptions);
    const _user: User | undefined = session?.user;

    if (!session || !_user || !_user._id) {
      return NextResponse.json(
        { success: false, message: 'Not authenticated' },
        { status: 401 }
      );
    }

    // Find user by ID
    const user = await UserModel.findOne({ where: { id: _user._id } });

    if (!user) {
      return NextResponse.json(
        { success: false, message: 'User not found' },
        { status: 404 }
      );
    }

    // Get messages JSON array from user
    let messagesRaw = user.get('messages');
    let messages: any[] = [];

    // Ensure messages is an array
    if (Array.isArray(messagesRaw)) {
      messages = messagesRaw;
    } else if (typeof messagesRaw === 'string') {
      try {
        const parsed = JSON.parse(messagesRaw);
        if (Array.isArray(parsed)) {
          messages = parsed;
        }
      } catch (e) {
        messages = [];
      }
    }

    // Sort messages by createdAt descending (latest first)
    messages.sort((a: any, b: any) => {
      const dateA = new Date(a.createdAt).getTime();
      const dateB = new Date(b.createdAt).getTime();
      return dateB - dateA;
    });

    return NextResponse.json(
      { success: true, messages },
      { status: 200 }
    );

  } catch (error) {
    console.error('Error fetching messages:', error);
    return NextResponse.json(
      { success: false, message: 'Internal Server Error' },
      { status: 500 }
    );
  }
}
