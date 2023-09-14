import type { ColumnType } from "kysely";

export type Generated<T> = T extends ColumnType<infer S, infer I, infer U>
  ? ColumnType<S, I | undefined, U>
  : ColumnType<T, T | undefined, T>;

export interface FileKeys {
  id: Generated<number>;
  user: string;
  file: string;
  key: Buffer;
}

export interface Files {
  id: string;
  name: string;
  owner: string;
  mime_type: string;
  uploaded: Generated<number>;
  metadata: Generated<Buffer | null>;
  creation_time: Date;
}

export interface DB {
  file_keys: FileKeys;
  files: Files;
}
