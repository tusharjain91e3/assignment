// sync.ts or main.ts
import sequelize from './db';
import User from './User';
import Message from './Message';

sequelize.sync({ alter: true }).then(() => {
  console.log('MySQL tables created!');
});
