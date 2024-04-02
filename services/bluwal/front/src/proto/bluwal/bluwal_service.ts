/* eslint-disable */
import Long from "long";
import type { CallContext, CallOptions } from "nice-grpc-common";
import _m0 from "protobufjs/minimal";
import {
  ChallengeSubmitRequest,
  ChallengeSubmitResponse,
  CheckGoalRequest,
  CheckGoalResponse,
  ClaimRewardRequest,
  ClaimRewardResponse,
  ContestCreateRequest,
  ContestCreateResponse,
  ContestEnrollRequest,
  ContestEnrollResponse,
  ContestGetRequest,
  ContestGetResponse,
  ContestListRequest,
  ContestListResponse,
} from "./bluwal";

export const protobufPackage = "bluwal";

export type BluwalServiceDefinition = typeof BluwalServiceDefinition;
export const BluwalServiceDefinition = {
  name: "BluwalService",
  fullName: "bluwal.BluwalService",
  methods: {
    contestCreate: {
      name: "ContestCreate",
      requestType: ContestCreateRequest,
      requestStream: false,
      responseType: ContestCreateResponse,
      responseStream: false,
      options: {},
    },
    contestGet: {
      name: "ContestGet",
      requestType: ContestGetRequest,
      requestStream: false,
      responseType: ContestGetResponse,
      responseStream: false,
      options: {},
    },
    contestList: {
      name: "ContestList",
      requestType: ContestListRequest,
      requestStream: false,
      responseType: ContestListResponse,
      responseStream: false,
      options: {},
    },
    contestEnroll: {
      name: "ContestEnroll",
      requestType: ContestEnrollRequest,
      requestStream: false,
      responseType: ContestEnrollResponse,
      responseStream: false,
      options: {},
    },
    challengeSubmit: {
      name: "ChallengeSubmit",
      requestType: ChallengeSubmitRequest,
      requestStream: false,
      responseType: ChallengeSubmitResponse,
      responseStream: false,
      options: {},
    },
    checkGoal: {
      name: "CheckGoal",
      requestType: CheckGoalRequest,
      requestStream: false,
      responseType: CheckGoalResponse,
      responseStream: false,
      options: {},
    },
    claimReward: {
      name: "ClaimReward",
      requestType: ClaimRewardRequest,
      requestStream: false,
      responseType: ClaimRewardResponse,
      responseStream: false,
      options: {},
    },
  },
} as const;

export interface BluwalServiceImplementation<CallContextExt = {}> {
  contestCreate(
    request: ContestCreateRequest,
    context: CallContext & CallContextExt,
  ): Promise<DeepPartial<ContestCreateResponse>>;
  contestGet(
    request: ContestGetRequest,
    context: CallContext & CallContextExt,
  ): Promise<DeepPartial<ContestGetResponse>>;
  contestList(
    request: ContestListRequest,
    context: CallContext & CallContextExt,
  ): Promise<DeepPartial<ContestListResponse>>;
  contestEnroll(
    request: ContestEnrollRequest,
    context: CallContext & CallContextExt,
  ): Promise<DeepPartial<ContestEnrollResponse>>;
  challengeSubmit(
    request: ChallengeSubmitRequest,
    context: CallContext & CallContextExt,
  ): Promise<DeepPartial<ChallengeSubmitResponse>>;
  checkGoal(request: CheckGoalRequest, context: CallContext & CallContextExt): Promise<DeepPartial<CheckGoalResponse>>;
  claimReward(
    request: ClaimRewardRequest,
    context: CallContext & CallContextExt,
  ): Promise<DeepPartial<ClaimRewardResponse>>;
}

export interface BluwalServiceClient<CallOptionsExt = {}> {
  contestCreate(
    request: DeepPartial<ContestCreateRequest>,
    options?: CallOptions & CallOptionsExt,
  ): Promise<ContestCreateResponse>;
  contestGet(
    request: DeepPartial<ContestGetRequest>,
    options?: CallOptions & CallOptionsExt,
  ): Promise<ContestGetResponse>;
  contestList(
    request: DeepPartial<ContestListRequest>,
    options?: CallOptions & CallOptionsExt,
  ): Promise<ContestListResponse>;
  contestEnroll(
    request: DeepPartial<ContestEnrollRequest>,
    options?: CallOptions & CallOptionsExt,
  ): Promise<ContestEnrollResponse>;
  challengeSubmit(
    request: DeepPartial<ChallengeSubmitRequest>,
    options?: CallOptions & CallOptionsExt,
  ): Promise<ChallengeSubmitResponse>;
  checkGoal(request: DeepPartial<CheckGoalRequest>, options?: CallOptions & CallOptionsExt): Promise<CheckGoalResponse>;
  claimReward(
    request: DeepPartial<ClaimRewardRequest>,
    options?: CallOptions & CallOptionsExt,
  ): Promise<ClaimRewardResponse>;
}

type Builtin = Date | Function | Uint8Array | string | number | boolean | undefined;

export type DeepPartial<T> = T extends Builtin ? T
  : T extends Long ? string | number | Long : T extends globalThis.Array<infer U> ? globalThis.Array<DeepPartial<U>>
  : T extends ReadonlyArray<infer U> ? ReadonlyArray<DeepPartial<U>>
  : T extends { $case: string } ? { [K in keyof Omit<T, "$case">]?: DeepPartial<T[K]> } & { $case: T["$case"] }
  : T extends {} ? { [K in keyof T]?: DeepPartial<T[K]> }
  : Partial<T>;

if (_m0.util.Long !== Long) {
  _m0.util.Long = Long as any;
  _m0.configure();
}
