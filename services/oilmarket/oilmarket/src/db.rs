use sqlx::{postgres::PgPoolOptions, self, PgPool};
use std::vec::Vec;
use uuid::Uuid;
use std::future::Future;
use tokio::time::{timeout, Timeout};

pub struct DB {
    pool: PgPool,
    request_timeout: std::time::Duration,
}

struct DbBuyer {
    id: i32,
    flag: String,
    name: String,
    api_key: Uuid,
    pub attesters: Vec<(i32, String, Uuid, String)>,
}


#[derive(Debug)]
pub struct Buyer {
    pub id: i32,
    pub flag: String,
    pub name: String,
    pub api_key: Uuid,
    pub attesters: Vec<Attester>,
}

#[derive(Debug,sqlx::Decode)]
pub struct Attester {
    pub id: i32,
    pub name: String,
    pub api_key: Uuid,
    pub key: String,
}

#[derive(Debug)]
pub struct Seller {
    pub id: i32,
    pub name: String,
    pub api_key: Uuid,
    pub barrels: Vec<i32>,
}

impl From<DbBuyer> for Buyer {
    fn from(value: DbBuyer) -> Self {
        Self {
            id: value.id,
            name: value.name,
            api_key: value.api_key,
            flag: value.flag,
            attesters: value
                .attesters
                .into_iter()
                .map(|(id, name, api_key, key)| Attester {
                    id,
                    name,
                    api_key,
                    key,
                })
                .collect()
        }
    }
}

impl DB {
    pub async fn connect(
        url: &str,
        connect_timeout: std::time::Duration,
        request_timeout: std::time::Duration,
        max_connections: u32,
    ) -> anyhow::Result<Self> {
        let pool = timeout(
            connect_timeout,
            PgPoolOptions::new()
                .max_connections(max_connections)
                .connect(url),
        )
        .await??;

        Ok(Self {
            pool,
            request_timeout,
        })
    }

    pub async fn create_attester(&self, name: &str, api_key: &Uuid, key: &str) -> anyhow::Result<bool> {
        let q = sqlx::query!(
            "INSERT INTO attesters
            (name, api_key, key)
            VALUES ($1, $2, $3)", 
            name,
            api_key,
            key,
        );
        match self.timeout(q.execute(&self.pool)).await? {
            Ok(_) => Ok(true),
            Err(sqlx::Error::Database(db_error)) if db_error.is_unique_violation() => Ok(false),
            Err(e) => Err(anyhow::Error::new(e)),

        }
    }

    pub async fn create_seller(&self, name: &str, api_key: &Uuid) -> anyhow::Result<bool> {
        let q = sqlx::query!(
            "INSERT INTO sellers
            (name, api_key)
            VALUES ($1, $2)", 
            name,
            api_key,
        );
        match self.timeout(q.execute(&self.pool)).await? {
            Ok(_) => Ok(true),
            Err(sqlx::Error::Database(db_error)) if db_error.is_unique_violation() => Ok(false),
            Err(e) => Err(anyhow::Error::new(e)),

        }
    }

    pub async fn add_barrel(&self, seller: &Seller) -> anyhow::Result<i32> {
        let q = sqlx::query!(
            "INSERT INTO barrels
            (seller_id)
            VALUES ($1)
            RETURNING id", 
            seller.id,
        );
        match self.timeout(q.fetch_one(&self.pool)).await? {
            Ok(query) => Ok(query.id),
            Err(e) => Err(anyhow::Error::new(e)),

        }
    }
    pub async fn remove_barrel(&self, barrel_id: i32) -> anyhow::Result<bool> {
        let q = sqlx::query!(
            "DELETE FROM barrels
            WHERE id = $1",
            barrel_id,
        );
        match self.timeout(q.execute(&self.pool)).await? {
            Ok(_) => Ok(true),
            Err(sqlx::Error::Database(db_error)) if db_error.is_check_violation() => Ok(false),
            Err(e) => Err(anyhow::Error::new(e)),

        }
    }

     pub async fn create_buyer(&self, name: &str, api_key: &Uuid, flag: &str, attesters: &[Attester]) -> anyhow::Result<bool> {

        let mut tx = self.timeout(self.pool.begin()).await??;

        let q = sqlx::query!(
            "INSERT INTO buyers
            (name, api_key, flag)
            VALUES ($1, $2, $3)
            RETURNING id",
            name,
            api_key,
            flag,
        );

        let buyer_id = match self.timeout(q.fetch_one(&mut *tx)).await? {
            Ok(query) => query.id,
            Err(sqlx::Error::Database(db_error)) if db_error.is_unique_violation() => return Ok(false),
            Err(e) => return Err(anyhow::Error::new(e)),
        };

        for attester in attesters.iter() {

            let q = sqlx::query!(
                "INSERT INTO buyer_attester
                (buyer_id, attester_id)
                VALUES ($1, $2)",
                buyer_id,
                attester.id,
            );

            self.timeout(q.execute(&mut *tx)).await??;
        }

        self.timeout(tx.commit()).await??;

        Ok(true)
    }

    pub async fn get_buyer_by_name(&self, name: &str) -> anyhow::Result<Option<Buyer>> {

        let q = sqlx::query_as!(
            DbBuyer,
            r#"SELECT
                b.id as id,
                b.name as name,
                b.api_key as api_key,
                b.flag as flag, 
                ARRAY_AGG(
                    ROW(
                        a.id,
                        a.name,
                        a.api_key,
                        a.key
                    )
                ) AS "attesters!: Vec<(i32, String, Uuid, String)>"
            FROM buyers b
            LEFT JOIN buyer_attester ba
            ON ba.buyer_id = b.id
            LEFT JOIN attesters a
            ON a.id = ba.attester_id
            WHERE b.name = $1
            GROUP BY b.id"#,
            name,
        );

        let db_buyer = match self.timeout(q.fetch_one(&self.pool)).await? {
            Ok(buyer) => buyer,
            Err(sqlx::Error::RowNotFound) => return Ok(None),
            Err(e) => return Err(anyhow::Error::new(e)),
        };

        Ok(Some(db_buyer.into()))
    }

    pub async fn get_attester_by_name(&self, name: &str) -> anyhow::Result<Option<Attester>> {
        let q = sqlx::query_as!(
            Attester,
            "SELECT id, name, api_key, key
            FROM attesters
            WHERE name = $1",
            name,
        );
        match self.timeout(q.fetch_one(&self.pool)).await? {
            Ok(attester) => Ok(Some(attester)),
            Err(sqlx::Error::RowNotFound) => Ok(None),
            Err(e) => Err(anyhow::Error::new(e)),
        }
    }

    pub async fn get_attester_by_api_key(&self, api_key: &Uuid) -> anyhow::Result<Option<Attester>> {
        let q = sqlx::query_as!(
            Attester,
            "SELECT id, name, api_key, key
            FROM attesters
            WHERE api_key = $1",
            api_key,
        );
        match self.timeout(q.fetch_one(&self.pool)).await? {
            Ok(attester) => Ok(Some(attester)),
            Err(sqlx::Error::RowNotFound) => Ok(None),
            Err(e) => Err(anyhow::Error::new(e)),
        }
    }

    pub async fn get_seller_by_api_key(&self, api_key: &Uuid) -> anyhow::Result<Option<Seller>> {
        let q = sqlx::query_as!(
            Seller,
            r#"SELECT
                s.id as id,
                s.name as name,
                s.api_key as api_key,
                ARRAY_REMOVE(ARRAY_AGG(
                    b.id
                ), NULL) AS "barrels!: Vec<i32>"
            FROM sellers s
            LEFT JOIN barrels b
            ON s.id = b.seller_id
            WHERE s.api_key = $1
            GROUP BY s.id"#,
            api_key,
        );
        match self.timeout(q.fetch_one(&self.pool)).await? {
            Ok(attester) => Ok(Some(attester)),
            Err(sqlx::Error::RowNotFound) => Ok(None),
            Err(e) => Err(anyhow::Error::new(e)),
        }
    }

    fn timeout<F>(&self, f: F) -> Timeout<F>
    where
        F: Future,
    {
        timeout(self.request_timeout, f)
    }

}
