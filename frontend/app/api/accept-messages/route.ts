import { getServerSession } from 'next-auth/next';
import { authOptions } from '../auth/[...nextauth]/options';
import sequelize from '@/models/db';
import UserModel from '@/models/User';
import { User } from 'next-auth';

export async function POST(request: Request) {
  // Connect to the database
  await sequelize.authenticate();

  const session = await getServerSession(authOptions);
  const user: User | undefined = session?.user;
  if (!session || !user) {
    return Response.json(
      { success: false, message: 'Not authenticated' },
      { status: 401 }
    );
  }

  const userId = user._id;
  const { acceptMessages } = await request.json();

  try {
    // Update the user's message acceptance status
    const userInstance = await UserModel.findOne({ where: { id: userId } });
    if (!userInstance) {
      // User not found, will be handled below
      return Response.json(
        {
          success: false,
          message: 'User not found',
        },
        { status: 404 }
      );
    }
    userInstance.isAcceptingMessaging = acceptMessages;
    await userInstance.save();
    const updatedUser = userInstance;

    if (!updatedUser) {
      // User not found
      return Response.json(
        {
          success: false,
          message: 'Unable to find user to update message acceptance status',
        },
        { status: 404 }
      );
    }

    // Successfully updated message acceptance status
    return Response.json(
      {
        success: true,
        message: 'Message acceptance status updated successfully',
        updatedUser,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error updating message acceptance status:', error);
    return Response.json(
      { success: false, message: 'Error updating message acceptance status' },
      { status: 500 }
    );
  }
}



export async function GET(request: Request) {
  // Connect to the database
  // @ts-ignore
  await sequelize.authenticate();

  // Get the user session
  // @ts-ignore
  const session = await getServerSession(authOptions);
  // @ts-ignore
  const user = session?.user;
  
  // Check if the user is authenticated
  if (!session || !user) {
    return Response.json(
      { success: false, message: 'Not authenticated' },
      { status: 401 }
    );
  }

  try {
    // Retrieve the user from the database using the ID
    const foundUser = await UserModel.findOne({ where: { id: user._id } });

    if (!foundUser) {
      // User not found
      return Response.json(
        { success: false, message: 'User not found' },
        { status: 404 }
      );
    }

    // Return the user's message acceptance status
    return Response.json(
      {
        success: true,
        isAcceptingMessages: foundUser.isAcceptingMessaging,
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Error retrieving message acceptance status:', error);
    return Response.json(
      { success: false, message: 'Error retrieving message acceptance status' },
      { status: 500 }
    );
  }
}