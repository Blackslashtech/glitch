import {grpcAddress} from "@/config.ts";
import {BluwalServiceClient, BluwalServiceDefinition,} from "@/proto/bluwal/bluwal_service.ts";
import {createChannel, createClient, WebsocketTransport} from "nice-grpc-web";

const channel = createChannel(grpcAddress, WebsocketTransport());

export const bluwalServiceClient: BluwalServiceClient = createClient(
    BluwalServiceDefinition,
    channel
);
