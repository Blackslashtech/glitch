use std::time::Duration;

use tonic::transport::Server;
use oilmarket::service;

use oilmarket::grpc::oilmarket_server::OilmarketServer;
use oilmarket::db::DB;

const DB_CONNECT_TIMEOUT: Duration = Duration::from_secs(5);
const DB_REQUEST_TIMEOUT: Duration = Duration::from_secs(5);
const DB_MAX_CONNECTIONS: u32 = 64;
const DB_URL: &str = "postgres://oilmarket:oilmarket@postgres/oilmarket";


#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let addr = "0.0.0.0:2112".parse()?;
    let service = service::Oilmarket::new(DB::connect(
        DB_URL,
        DB_CONNECT_TIMEOUT,
        DB_REQUEST_TIMEOUT,
        DB_MAX_CONNECTIONS,
    ).await? );

    println!("listening on {}", addr);

    Server::builder()
        .add_service(OilmarketServer::new(service))
        .serve(addr)
        .await?;

    Ok(())
}
