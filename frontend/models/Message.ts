import { DataTypes, Model, Optional } from 'sequelize';
import sequelize from './db';

interface MessageAttributes {
  id: number;
  userId: number;
  content: string;
  createdAt: Date;
}

type MessageCreationAttributes = Optional<MessageAttributes, 'id' | 'createdAt'>;

class Message extends Model<MessageAttributes, MessageCreationAttributes> implements MessageAttributes {
  public id!: number;
  public userId!: number;
  public content!: string;
  public createdAt!: Date;
}

Message.init(
  {
    id: {
      type: DataTypes.INTEGER.UNSIGNED,
      autoIncrement: true,
      primaryKey: true,
    },
    userId: {
      type: DataTypes.INTEGER.UNSIGNED,
      allowNull: false,
    },
    content: {
      type: DataTypes.TEXT,
      allowNull: false,
    },
    createdAt: {
      type: DataTypes.DATE,
      defaultValue: DataTypes.NOW,
    },
  },
  {
    sequelize,
    modelName: 'Message',
    tableName: 'messages',
    timestamps: false,
  }
);

export default Message;
