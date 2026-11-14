import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';
export const packingLists = sqliteTable('packing_lists', {
 userId: text('user_id').primaryKey(),
 document: text('document').notNull(),
 revision: integer('revision').notNull().default(0),
});
