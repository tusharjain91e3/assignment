import { Sequelize } from 'sequelize';

const sequelize = new Sequelize(
  process.env.MYSQL_DATABASE || 'ecommercedb',
  process.env.MYSQL_USER || 'root',
  process.env.MYSQL_PASSWORD || 'password',
  {
    host: process.env.MYSQL_HOST || 'localhost',
    dialect: 'mysql',
    port: Number(process.env.MYSQL_PORT) || 3306,
    logging: false,
  }
);

export default sequelize;
