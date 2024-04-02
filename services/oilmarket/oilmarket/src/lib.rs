pub mod crypto;

pub mod db;

pub mod grpc {
    tonic::include_proto!("oilmarket");
}

pub mod service;
