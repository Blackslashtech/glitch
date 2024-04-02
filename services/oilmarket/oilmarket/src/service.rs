use std::str::FromStr;

use tonic::{Request, Response, Status, async_trait};
use uuid::Uuid;
use serde_json;
use serde::{Deserialize,Serialize};
use std::error::Error;
use crate::{grpc, crypto};
use crate::db::DB;

pub struct Oilmarket {
    db: DB,
}

#[derive(Serialize, Deserialize, Debug)]
struct SellRequest {
    barrel_id: i32,
}

fn anyhow_to_status(err: anyhow::Error) -> Status {
    Status::internal(err.to_string())
}

fn err_to_status(err: impl Error) -> Status {
    Status::internal(err.to_string())
}

fn parse_api_key(api_key: &str) -> Result<Uuid, Status> {
    match Uuid::from_str(api_key) {
        Ok(uuid) => Ok(uuid),
        Err(_) => Err(Status::unauthenticated("invalid uuid")),
    }
}

impl Oilmarket {
    pub fn new(db: DB) -> Self {
        Self {
            db
        }
    }
}

#[async_trait]
impl grpc::oilmarket_server::Oilmarket for Oilmarket {
    async fn sign(
        &self,
        request: Request<grpc::SignRequest>,
    ) -> Result<Response<grpc::SignResponse>, Status> {
        let request_body = request.into_inner();

        let api_key = parse_api_key(&request_body.api_key)?;

        let attester = match self.db.get_attester_by_api_key(&api_key).await.map_err(anyhow_to_status)? {
            Some(attester) => attester,
            None => return Err(Status::unauthenticated("invalid api key")),
        };

        let key: crypto::Key = serde_json::from_str(&attester.key).map_err(err_to_status)?;
        let signature = key.sign(&request_body.request);
        let resp = grpc::SignResponse {
            signature,
        };

        Ok(Response::new(resp))
        
    }

    async fn sell(
        &self,
        request: Request<grpc::SellRequest>,
    ) -> Result<Response<grpc::SellResponse>, Status> {

        let request_body = request.into_inner();

        let api_key = parse_api_key(&request_body.api_key)?;


        let seller = match self.db.get_seller_by_api_key(&api_key).await.map_err(anyhow_to_status)? {
            Some(seller) => seller,
            None => return Err(Status::unauthenticated("invalid api key")),
        };
        let buyer = match self.db.get_buyer_by_name(&request_body.buyer).await.map_err(anyhow_to_status)? {
            Some(buyer) => buyer,
            None => return Err(Status::not_found(format!("buyer {} does not exist", request_body.buyer))),
        };
        let attester = match self.db
            .get_attester_by_name(&request_body.attester)
            .await.map_err(anyhow_to_status)? {
            Some(attester) => attester,
            None => return Err(
                    Status::not_found(format!("attester {} does not exist", request_body.attester))
                ),
        };

        if buyer.attesters.iter().filter(|ba| ba.name == attester.name).count() == 0 {
            return Err(Status::permission_denied("buyer does not accept this attester"));
        }

        let key: crypto::Key = serde_json::from_str(&attester.key).map_err(err_to_status)?;
        if !key.verify(&request_body.signature, &request_body.request) {
            return Err(Status::permission_denied("signature verification failed"));
        }
        let sell_request: SellRequest = serde_json::from_slice(&request_body.request).map_err(err_to_status)?;

        if !seller.barrels.iter().any(|b| *b == sell_request.barrel_id) {
            return Err(Status::permission_denied("you do not own this barrel"));
        }

        self.db.remove_barrel(sell_request.barrel_id).await.map_err(anyhow_to_status)?;

        let resp = grpc::SellResponse {
            flag: buyer.flag,
        };

        Ok(Response::new(resp))

    }
    async fn create_buyer(
        &self,
        request: Request<grpc::CreateBuyerRequest>,
    ) -> Result<Response<grpc::ApiKeyResponse>, Status> {

        let request_body = request.into_inner();

        let mut attesters = Vec::new();

        if request_body.attesters.is_empty() {
            return Err(Status::invalid_argument("at least one attester must be present"))
        }

        for attester_name in request_body.attesters.iter() {
            match self.db.get_attester_by_name(attester_name).await.map_err(anyhow_to_status)? {
                Some(attester) => attesters.push(attester),
                None => return Err(Status::not_found(format!("attester {attester_name} does not exist"))),
            };
        }

        let api_key = Uuid::new_v4();
        if !self.db
            .create_buyer(&request_body.name, &api_key, &request_body.flag, &attesters)
            .await.map_err(anyhow_to_status)? {
            Err(Status::already_exists("buyer with this name already exists"))
        } else {
            let resp = grpc::ApiKeyResponse {
                api_key: api_key.into(),
            };
            Ok(Response::new(resp))
        }

    }
    async fn create_attester(
        &self,
        request: Request<grpc::CreateAttesterRequest>,
    ) -> Result<Response<grpc::ApiKeyResponse>, Status> {
        let request_body = request.into_inner();

        let key = serde_json::to_string(&crypto::Key::random_key()).map_err(err_to_status)?;
        let api_key = Uuid::new_v4();

        if !self.db.create_attester(&request_body.name, &api_key, &key).await.map_err(anyhow_to_status)? {
            Err(Status::already_exists("seller with this name already exists"))
        } else {
            let resp = grpc::ApiKeyResponse {
                api_key: api_key.into(),
            };
            Ok(Response::new(resp))
        }
    }

    async fn create_seller(
        &self,
        request: Request<grpc::CreateSellerRequest>,
    ) -> Result<Response<grpc::ApiKeyResponse>, Status> {
        let request_body = request.into_inner();
        let api_key = Uuid::new_v4();

        if !self.db.create_seller(&request_body.name, &api_key).await.map_err(anyhow_to_status)? {
            Err(Status::already_exists("seller with this name already exists"))
        } else {
            let resp = grpc::ApiKeyResponse {
                api_key: api_key.into(),
            };
            Ok(Response::new(resp))
        }
    }

    async fn add_barrel(
        &self,
        request: Request<grpc::AddBarrelRequest>,
    ) -> Result<
    Response<grpc::AddBarrelResponse>,
    Status,
    > {
        let request_body = request.into_inner();
        let api_key = parse_api_key(&request_body.api_key)?;
        let seller = match self.db.get_seller_by_api_key(&api_key).await.map_err(anyhow_to_status)? {
            Some(seller) => seller,
            None => return Err(Status::unauthenticated("invalid api key")),
        };
        let barrel_id = self.db.add_barrel(&seller).await.map_err(anyhow_to_status)?;

        let resp = grpc::AddBarrelResponse {
            id: barrel_id
        };

        Ok(Response::new(resp))
    }

}

