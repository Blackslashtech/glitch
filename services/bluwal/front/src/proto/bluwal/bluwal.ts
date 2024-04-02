/* eslint-disable */
import Long from "long";
import _m0 from "protobufjs/minimal";

export const protobufPackage = "bluwal";

export interface FactorChallenge {
  n: string;
}

export interface FactorChallengeSubmission {
  factors: string[];
}

export interface Challenge {
  challenge?: { $case: "factorChallenge"; factorChallenge: FactorChallenge } | undefined;
  characteristic: number;
  delta: number;
}

export interface Contest {
  id: string;
  author: string;
  goal: number[];
  threshold: number[];
  challenges: Challenge[];
  reward: string;
}

export interface EnrollmentFilter {
  contestId: string;
  userId: string;
  currentState: number[];
}

export interface ContestCreateRequest {
  contest: Contest | undefined;
}

export interface ContestCreateResponse {
  contest: Contest | undefined;
}

export interface ContestGetRequest {
  id: string;
  author: string;
}

export interface ContestGetResponse {
  contest: Contest | undefined;
}

export interface ContestEnrollRequest {
  enrollmentFilter: EnrollmentFilter | undefined;
}

export interface ContestEnrollResponse {
  enrollmentFilter: EnrollmentFilter | undefined;
}

export interface ChallengeSubmitRequest {
  enrollmentFilter: EnrollmentFilter | undefined;
  submission?: { $case: "factorChallengeSubmission"; factorChallengeSubmission: FactorChallengeSubmission } | undefined;
}

export interface ChallengeSubmitResponse {
  enrollmentFilter: EnrollmentFilter | undefined;
  currentChallenge: number;
}

export interface CheckGoalRequest {
  enrollmentFilter: EnrollmentFilter | undefined;
}

export interface CheckGoalResponse {
  currentChallenge: number;
  currentState: number[];
}

export interface ClaimRewardRequest {
  enrollmentFilter: EnrollmentFilter | undefined;
}

export interface ClaimRewardResponse {
  reward: string;
}

export interface ContestListRequest {
  author: string;
  limit: number;
  offset: number;
}

export interface ContestListResponse {
  contests: Contest[];
}

function createBaseFactorChallenge(): FactorChallenge {
  return { n: "" };
}

export const FactorChallenge = {
  encode(message: FactorChallenge, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.n !== "") {
      writer.uint32(10).string(message.n);
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): FactorChallenge {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseFactorChallenge();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.n = reader.string();
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): FactorChallenge {
    return { n: isSet(object.n) ? globalThis.String(object.n) : "" };
  },

  toJSON(message: FactorChallenge): unknown {
    const obj: any = {};
    if (message.n !== "") {
      obj.n = message.n;
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<FactorChallenge>, I>>(base?: I): FactorChallenge {
    return FactorChallenge.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<FactorChallenge>, I>>(object: I): FactorChallenge {
    const message = createBaseFactorChallenge();
    message.n = object.n ?? "";
    return message;
  },
};

function createBaseFactorChallengeSubmission(): FactorChallengeSubmission {
  return { factors: [] };
}

export const FactorChallengeSubmission = {
  encode(message: FactorChallengeSubmission, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    for (const v of message.factors) {
      writer.uint32(10).string(v!);
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): FactorChallengeSubmission {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseFactorChallengeSubmission();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.factors.push(reader.string());
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): FactorChallengeSubmission {
    return {
      factors: globalThis.Array.isArray(object?.factors) ? object.factors.map((e: any) => globalThis.String(e)) : [],
    };
  },

  toJSON(message: FactorChallengeSubmission): unknown {
    const obj: any = {};
    if (message.factors?.length) {
      obj.factors = message.factors;
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<FactorChallengeSubmission>, I>>(base?: I): FactorChallengeSubmission {
    return FactorChallengeSubmission.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<FactorChallengeSubmission>, I>>(object: I): FactorChallengeSubmission {
    const message = createBaseFactorChallengeSubmission();
    message.factors = object.factors?.map((e) => e) || [];
    return message;
  },
};

function createBaseChallenge(): Challenge {
  return { challenge: undefined, characteristic: 0, delta: 0 };
}

export const Challenge = {
  encode(message: Challenge, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    switch (message.challenge?.$case) {
      case "factorChallenge":
        FactorChallenge.encode(message.challenge.factorChallenge, writer.uint32(10).fork()).ldelim();
        break;
    }
    if (message.characteristic !== 0) {
      writer.uint32(16).int32(message.characteristic);
    }
    if (message.delta !== 0) {
      writer.uint32(24).int32(message.delta);
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): Challenge {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseChallenge();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.challenge = {
            $case: "factorChallenge",
            factorChallenge: FactorChallenge.decode(reader, reader.uint32()),
          };
          continue;
        case 2:
          if (tag !== 16) {
            break;
          }

          message.characteristic = reader.int32();
          continue;
        case 3:
          if (tag !== 24) {
            break;
          }

          message.delta = reader.int32();
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): Challenge {
    return {
      challenge: isSet(object.factorChallenge)
        ? { $case: "factorChallenge", factorChallenge: FactorChallenge.fromJSON(object.factorChallenge) }
        : undefined,
      characteristic: isSet(object.characteristic) ? globalThis.Number(object.characteristic) : 0,
      delta: isSet(object.delta) ? globalThis.Number(object.delta) : 0,
    };
  },

  toJSON(message: Challenge): unknown {
    const obj: any = {};
    if (message.challenge?.$case === "factorChallenge") {
      obj.factorChallenge = FactorChallenge.toJSON(message.challenge.factorChallenge);
    }
    if (message.characteristic !== 0) {
      obj.characteristic = Math.round(message.characteristic);
    }
    if (message.delta !== 0) {
      obj.delta = Math.round(message.delta);
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<Challenge>, I>>(base?: I): Challenge {
    return Challenge.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<Challenge>, I>>(object: I): Challenge {
    const message = createBaseChallenge();
    if (
      object.challenge?.$case === "factorChallenge" &&
      object.challenge?.factorChallenge !== undefined &&
      object.challenge?.factorChallenge !== null
    ) {
      message.challenge = {
        $case: "factorChallenge",
        factorChallenge: FactorChallenge.fromPartial(object.challenge.factorChallenge),
      };
    }
    message.characteristic = object.characteristic ?? 0;
    message.delta = object.delta ?? 0;
    return message;
  },
};

function createBaseContest(): Contest {
  return { id: "", author: "", goal: [], threshold: [], challenges: [], reward: "" };
}

export const Contest = {
  encode(message: Contest, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.id !== "") {
      writer.uint32(10).string(message.id);
    }
    if (message.author !== "") {
      writer.uint32(18).string(message.author);
    }
    writer.uint32(26).fork();
    for (const v of message.goal) {
      writer.int32(v);
    }
    writer.ldelim();
    writer.uint32(34).fork();
    for (const v of message.threshold) {
      writer.int32(v);
    }
    writer.ldelim();
    for (const v of message.challenges) {
      Challenge.encode(v!, writer.uint32(42).fork()).ldelim();
    }
    if (message.reward !== "") {
      writer.uint32(50).string(message.reward);
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): Contest {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseContest();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.id = reader.string();
          continue;
        case 2:
          if (tag !== 18) {
            break;
          }

          message.author = reader.string();
          continue;
        case 3:
          if (tag === 24) {
            message.goal.push(reader.int32());

            continue;
          }

          if (tag === 26) {
            const end2 = reader.uint32() + reader.pos;
            while (reader.pos < end2) {
              message.goal.push(reader.int32());
            }

            continue;
          }

          break;
        case 4:
          if (tag === 32) {
            message.threshold.push(reader.int32());

            continue;
          }

          if (tag === 34) {
            const end2 = reader.uint32() + reader.pos;
            while (reader.pos < end2) {
              message.threshold.push(reader.int32());
            }

            continue;
          }

          break;
        case 5:
          if (tag !== 42) {
            break;
          }

          message.challenges.push(Challenge.decode(reader, reader.uint32()));
          continue;
        case 6:
          if (tag !== 50) {
            break;
          }

          message.reward = reader.string();
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): Contest {
    return {
      id: isSet(object.id) ? globalThis.String(object.id) : "",
      author: isSet(object.author) ? globalThis.String(object.author) : "",
      goal: globalThis.Array.isArray(object?.goal) ? object.goal.map((e: any) => globalThis.Number(e)) : [],
      threshold: globalThis.Array.isArray(object?.threshold)
        ? object.threshold.map((e: any) => globalThis.Number(e))
        : [],
      challenges: globalThis.Array.isArray(object?.challenges)
        ? object.challenges.map((e: any) => Challenge.fromJSON(e))
        : [],
      reward: isSet(object.reward) ? globalThis.String(object.reward) : "",
    };
  },

  toJSON(message: Contest): unknown {
    const obj: any = {};
    if (message.id !== "") {
      obj.id = message.id;
    }
    if (message.author !== "") {
      obj.author = message.author;
    }
    if (message.goal?.length) {
      obj.goal = message.goal.map((e) => Math.round(e));
    }
    if (message.threshold?.length) {
      obj.threshold = message.threshold.map((e) => Math.round(e));
    }
    if (message.challenges?.length) {
      obj.challenges = message.challenges.map((e) => Challenge.toJSON(e));
    }
    if (message.reward !== "") {
      obj.reward = message.reward;
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<Contest>, I>>(base?: I): Contest {
    return Contest.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<Contest>, I>>(object: I): Contest {
    const message = createBaseContest();
    message.id = object.id ?? "";
    message.author = object.author ?? "";
    message.goal = object.goal?.map((e) => e) || [];
    message.threshold = object.threshold?.map((e) => e) || [];
    message.challenges = object.challenges?.map((e) => Challenge.fromPartial(e)) || [];
    message.reward = object.reward ?? "";
    return message;
  },
};

function createBaseEnrollmentFilter(): EnrollmentFilter {
  return { contestId: "", userId: "", currentState: [] };
}

export const EnrollmentFilter = {
  encode(message: EnrollmentFilter, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.contestId !== "") {
      writer.uint32(10).string(message.contestId);
    }
    if (message.userId !== "") {
      writer.uint32(18).string(message.userId);
    }
    writer.uint32(26).fork();
    for (const v of message.currentState) {
      writer.int32(v);
    }
    writer.ldelim();
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): EnrollmentFilter {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseEnrollmentFilter();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.contestId = reader.string();
          continue;
        case 2:
          if (tag !== 18) {
            break;
          }

          message.userId = reader.string();
          continue;
        case 3:
          if (tag === 24) {
            message.currentState.push(reader.int32());

            continue;
          }

          if (tag === 26) {
            const end2 = reader.uint32() + reader.pos;
            while (reader.pos < end2) {
              message.currentState.push(reader.int32());
            }

            continue;
          }

          break;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): EnrollmentFilter {
    return {
      contestId: isSet(object.contestId) ? globalThis.String(object.contestId) : "",
      userId: isSet(object.userId) ? globalThis.String(object.userId) : "",
      currentState: globalThis.Array.isArray(object?.currentState)
        ? object.currentState.map((e: any) => globalThis.Number(e))
        : [],
    };
  },

  toJSON(message: EnrollmentFilter): unknown {
    const obj: any = {};
    if (message.contestId !== "") {
      obj.contestId = message.contestId;
    }
    if (message.userId !== "") {
      obj.userId = message.userId;
    }
    if (message.currentState?.length) {
      obj.currentState = message.currentState.map((e) => Math.round(e));
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<EnrollmentFilter>, I>>(base?: I): EnrollmentFilter {
    return EnrollmentFilter.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<EnrollmentFilter>, I>>(object: I): EnrollmentFilter {
    const message = createBaseEnrollmentFilter();
    message.contestId = object.contestId ?? "";
    message.userId = object.userId ?? "";
    message.currentState = object.currentState?.map((e) => e) || [];
    return message;
  },
};

function createBaseContestCreateRequest(): ContestCreateRequest {
  return { contest: undefined };
}

export const ContestCreateRequest = {
  encode(message: ContestCreateRequest, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.contest !== undefined) {
      Contest.encode(message.contest, writer.uint32(10).fork()).ldelim();
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ContestCreateRequest {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseContestCreateRequest();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.contest = Contest.decode(reader, reader.uint32());
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ContestCreateRequest {
    return { contest: isSet(object.contest) ? Contest.fromJSON(object.contest) : undefined };
  },

  toJSON(message: ContestCreateRequest): unknown {
    const obj: any = {};
    if (message.contest !== undefined) {
      obj.contest = Contest.toJSON(message.contest);
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ContestCreateRequest>, I>>(base?: I): ContestCreateRequest {
    return ContestCreateRequest.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ContestCreateRequest>, I>>(object: I): ContestCreateRequest {
    const message = createBaseContestCreateRequest();
    message.contest = (object.contest !== undefined && object.contest !== null)
      ? Contest.fromPartial(object.contest)
      : undefined;
    return message;
  },
};

function createBaseContestCreateResponse(): ContestCreateResponse {
  return { contest: undefined };
}

export const ContestCreateResponse = {
  encode(message: ContestCreateResponse, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.contest !== undefined) {
      Contest.encode(message.contest, writer.uint32(10).fork()).ldelim();
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ContestCreateResponse {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseContestCreateResponse();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.contest = Contest.decode(reader, reader.uint32());
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ContestCreateResponse {
    return { contest: isSet(object.contest) ? Contest.fromJSON(object.contest) : undefined };
  },

  toJSON(message: ContestCreateResponse): unknown {
    const obj: any = {};
    if (message.contest !== undefined) {
      obj.contest = Contest.toJSON(message.contest);
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ContestCreateResponse>, I>>(base?: I): ContestCreateResponse {
    return ContestCreateResponse.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ContestCreateResponse>, I>>(object: I): ContestCreateResponse {
    const message = createBaseContestCreateResponse();
    message.contest = (object.contest !== undefined && object.contest !== null)
      ? Contest.fromPartial(object.contest)
      : undefined;
    return message;
  },
};

function createBaseContestGetRequest(): ContestGetRequest {
  return { id: "", author: "" };
}

export const ContestGetRequest = {
  encode(message: ContestGetRequest, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.id !== "") {
      writer.uint32(10).string(message.id);
    }
    if (message.author !== "") {
      writer.uint32(18).string(message.author);
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ContestGetRequest {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseContestGetRequest();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.id = reader.string();
          continue;
        case 2:
          if (tag !== 18) {
            break;
          }

          message.author = reader.string();
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ContestGetRequest {
    return {
      id: isSet(object.id) ? globalThis.String(object.id) : "",
      author: isSet(object.author) ? globalThis.String(object.author) : "",
    };
  },

  toJSON(message: ContestGetRequest): unknown {
    const obj: any = {};
    if (message.id !== "") {
      obj.id = message.id;
    }
    if (message.author !== "") {
      obj.author = message.author;
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ContestGetRequest>, I>>(base?: I): ContestGetRequest {
    return ContestGetRequest.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ContestGetRequest>, I>>(object: I): ContestGetRequest {
    const message = createBaseContestGetRequest();
    message.id = object.id ?? "";
    message.author = object.author ?? "";
    return message;
  },
};

function createBaseContestGetResponse(): ContestGetResponse {
  return { contest: undefined };
}

export const ContestGetResponse = {
  encode(message: ContestGetResponse, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.contest !== undefined) {
      Contest.encode(message.contest, writer.uint32(10).fork()).ldelim();
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ContestGetResponse {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseContestGetResponse();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.contest = Contest.decode(reader, reader.uint32());
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ContestGetResponse {
    return { contest: isSet(object.contest) ? Contest.fromJSON(object.contest) : undefined };
  },

  toJSON(message: ContestGetResponse): unknown {
    const obj: any = {};
    if (message.contest !== undefined) {
      obj.contest = Contest.toJSON(message.contest);
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ContestGetResponse>, I>>(base?: I): ContestGetResponse {
    return ContestGetResponse.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ContestGetResponse>, I>>(object: I): ContestGetResponse {
    const message = createBaseContestGetResponse();
    message.contest = (object.contest !== undefined && object.contest !== null)
      ? Contest.fromPartial(object.contest)
      : undefined;
    return message;
  },
};

function createBaseContestEnrollRequest(): ContestEnrollRequest {
  return { enrollmentFilter: undefined };
}

export const ContestEnrollRequest = {
  encode(message: ContestEnrollRequest, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.enrollmentFilter !== undefined) {
      EnrollmentFilter.encode(message.enrollmentFilter, writer.uint32(10).fork()).ldelim();
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ContestEnrollRequest {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseContestEnrollRequest();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.enrollmentFilter = EnrollmentFilter.decode(reader, reader.uint32());
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ContestEnrollRequest {
    return {
      enrollmentFilter: isSet(object.enrollmentFilter) ? EnrollmentFilter.fromJSON(object.enrollmentFilter) : undefined,
    };
  },

  toJSON(message: ContestEnrollRequest): unknown {
    const obj: any = {};
    if (message.enrollmentFilter !== undefined) {
      obj.enrollmentFilter = EnrollmentFilter.toJSON(message.enrollmentFilter);
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ContestEnrollRequest>, I>>(base?: I): ContestEnrollRequest {
    return ContestEnrollRequest.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ContestEnrollRequest>, I>>(object: I): ContestEnrollRequest {
    const message = createBaseContestEnrollRequest();
    message.enrollmentFilter = (object.enrollmentFilter !== undefined && object.enrollmentFilter !== null)
      ? EnrollmentFilter.fromPartial(object.enrollmentFilter)
      : undefined;
    return message;
  },
};

function createBaseContestEnrollResponse(): ContestEnrollResponse {
  return { enrollmentFilter: undefined };
}

export const ContestEnrollResponse = {
  encode(message: ContestEnrollResponse, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.enrollmentFilter !== undefined) {
      EnrollmentFilter.encode(message.enrollmentFilter, writer.uint32(10).fork()).ldelim();
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ContestEnrollResponse {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseContestEnrollResponse();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.enrollmentFilter = EnrollmentFilter.decode(reader, reader.uint32());
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ContestEnrollResponse {
    return {
      enrollmentFilter: isSet(object.enrollmentFilter) ? EnrollmentFilter.fromJSON(object.enrollmentFilter) : undefined,
    };
  },

  toJSON(message: ContestEnrollResponse): unknown {
    const obj: any = {};
    if (message.enrollmentFilter !== undefined) {
      obj.enrollmentFilter = EnrollmentFilter.toJSON(message.enrollmentFilter);
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ContestEnrollResponse>, I>>(base?: I): ContestEnrollResponse {
    return ContestEnrollResponse.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ContestEnrollResponse>, I>>(object: I): ContestEnrollResponse {
    const message = createBaseContestEnrollResponse();
    message.enrollmentFilter = (object.enrollmentFilter !== undefined && object.enrollmentFilter !== null)
      ? EnrollmentFilter.fromPartial(object.enrollmentFilter)
      : undefined;
    return message;
  },
};

function createBaseChallengeSubmitRequest(): ChallengeSubmitRequest {
  return { enrollmentFilter: undefined, submission: undefined };
}

export const ChallengeSubmitRequest = {
  encode(message: ChallengeSubmitRequest, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.enrollmentFilter !== undefined) {
      EnrollmentFilter.encode(message.enrollmentFilter, writer.uint32(10).fork()).ldelim();
    }
    switch (message.submission?.$case) {
      case "factorChallengeSubmission":
        FactorChallengeSubmission.encode(message.submission.factorChallengeSubmission, writer.uint32(18).fork())
          .ldelim();
        break;
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ChallengeSubmitRequest {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseChallengeSubmitRequest();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.enrollmentFilter = EnrollmentFilter.decode(reader, reader.uint32());
          continue;
        case 2:
          if (tag !== 18) {
            break;
          }

          message.submission = {
            $case: "factorChallengeSubmission",
            factorChallengeSubmission: FactorChallengeSubmission.decode(reader, reader.uint32()),
          };
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ChallengeSubmitRequest {
    return {
      enrollmentFilter: isSet(object.enrollmentFilter) ? EnrollmentFilter.fromJSON(object.enrollmentFilter) : undefined,
      submission: isSet(object.factorChallengeSubmission)
        ? {
          $case: "factorChallengeSubmission",
          factorChallengeSubmission: FactorChallengeSubmission.fromJSON(object.factorChallengeSubmission),
        }
        : undefined,
    };
  },

  toJSON(message: ChallengeSubmitRequest): unknown {
    const obj: any = {};
    if (message.enrollmentFilter !== undefined) {
      obj.enrollmentFilter = EnrollmentFilter.toJSON(message.enrollmentFilter);
    }
    if (message.submission?.$case === "factorChallengeSubmission") {
      obj.factorChallengeSubmission = FactorChallengeSubmission.toJSON(message.submission.factorChallengeSubmission);
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ChallengeSubmitRequest>, I>>(base?: I): ChallengeSubmitRequest {
    return ChallengeSubmitRequest.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ChallengeSubmitRequest>, I>>(object: I): ChallengeSubmitRequest {
    const message = createBaseChallengeSubmitRequest();
    message.enrollmentFilter = (object.enrollmentFilter !== undefined && object.enrollmentFilter !== null)
      ? EnrollmentFilter.fromPartial(object.enrollmentFilter)
      : undefined;
    if (
      object.submission?.$case === "factorChallengeSubmission" &&
      object.submission?.factorChallengeSubmission !== undefined &&
      object.submission?.factorChallengeSubmission !== null
    ) {
      message.submission = {
        $case: "factorChallengeSubmission",
        factorChallengeSubmission: FactorChallengeSubmission.fromPartial(object.submission.factorChallengeSubmission),
      };
    }
    return message;
  },
};

function createBaseChallengeSubmitResponse(): ChallengeSubmitResponse {
  return { enrollmentFilter: undefined, currentChallenge: 0 };
}

export const ChallengeSubmitResponse = {
  encode(message: ChallengeSubmitResponse, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.enrollmentFilter !== undefined) {
      EnrollmentFilter.encode(message.enrollmentFilter, writer.uint32(10).fork()).ldelim();
    }
    if (message.currentChallenge !== 0) {
      writer.uint32(16).int32(message.currentChallenge);
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ChallengeSubmitResponse {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseChallengeSubmitResponse();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.enrollmentFilter = EnrollmentFilter.decode(reader, reader.uint32());
          continue;
        case 2:
          if (tag !== 16) {
            break;
          }

          message.currentChallenge = reader.int32();
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ChallengeSubmitResponse {
    return {
      enrollmentFilter: isSet(object.enrollmentFilter) ? EnrollmentFilter.fromJSON(object.enrollmentFilter) : undefined,
      currentChallenge: isSet(object.currentChallenge) ? globalThis.Number(object.currentChallenge) : 0,
    };
  },

  toJSON(message: ChallengeSubmitResponse): unknown {
    const obj: any = {};
    if (message.enrollmentFilter !== undefined) {
      obj.enrollmentFilter = EnrollmentFilter.toJSON(message.enrollmentFilter);
    }
    if (message.currentChallenge !== 0) {
      obj.currentChallenge = Math.round(message.currentChallenge);
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ChallengeSubmitResponse>, I>>(base?: I): ChallengeSubmitResponse {
    return ChallengeSubmitResponse.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ChallengeSubmitResponse>, I>>(object: I): ChallengeSubmitResponse {
    const message = createBaseChallengeSubmitResponse();
    message.enrollmentFilter = (object.enrollmentFilter !== undefined && object.enrollmentFilter !== null)
      ? EnrollmentFilter.fromPartial(object.enrollmentFilter)
      : undefined;
    message.currentChallenge = object.currentChallenge ?? 0;
    return message;
  },
};

function createBaseCheckGoalRequest(): CheckGoalRequest {
  return { enrollmentFilter: undefined };
}

export const CheckGoalRequest = {
  encode(message: CheckGoalRequest, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.enrollmentFilter !== undefined) {
      EnrollmentFilter.encode(message.enrollmentFilter, writer.uint32(10).fork()).ldelim();
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): CheckGoalRequest {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseCheckGoalRequest();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.enrollmentFilter = EnrollmentFilter.decode(reader, reader.uint32());
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): CheckGoalRequest {
    return {
      enrollmentFilter: isSet(object.enrollmentFilter) ? EnrollmentFilter.fromJSON(object.enrollmentFilter) : undefined,
    };
  },

  toJSON(message: CheckGoalRequest): unknown {
    const obj: any = {};
    if (message.enrollmentFilter !== undefined) {
      obj.enrollmentFilter = EnrollmentFilter.toJSON(message.enrollmentFilter);
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<CheckGoalRequest>, I>>(base?: I): CheckGoalRequest {
    return CheckGoalRequest.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<CheckGoalRequest>, I>>(object: I): CheckGoalRequest {
    const message = createBaseCheckGoalRequest();
    message.enrollmentFilter = (object.enrollmentFilter !== undefined && object.enrollmentFilter !== null)
      ? EnrollmentFilter.fromPartial(object.enrollmentFilter)
      : undefined;
    return message;
  },
};

function createBaseCheckGoalResponse(): CheckGoalResponse {
  return { currentChallenge: 0, currentState: [] };
}

export const CheckGoalResponse = {
  encode(message: CheckGoalResponse, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.currentChallenge !== 0) {
      writer.uint32(8).int32(message.currentChallenge);
    }
    writer.uint32(18).fork();
    for (const v of message.currentState) {
      writer.int32(v);
    }
    writer.ldelim();
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): CheckGoalResponse {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseCheckGoalResponse();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 8) {
            break;
          }

          message.currentChallenge = reader.int32();
          continue;
        case 2:
          if (tag === 16) {
            message.currentState.push(reader.int32());

            continue;
          }

          if (tag === 18) {
            const end2 = reader.uint32() + reader.pos;
            while (reader.pos < end2) {
              message.currentState.push(reader.int32());
            }

            continue;
          }

          break;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): CheckGoalResponse {
    return {
      currentChallenge: isSet(object.currentChallenge) ? globalThis.Number(object.currentChallenge) : 0,
      currentState: globalThis.Array.isArray(object?.currentState)
        ? object.currentState.map((e: any) => globalThis.Number(e))
        : [],
    };
  },

  toJSON(message: CheckGoalResponse): unknown {
    const obj: any = {};
    if (message.currentChallenge !== 0) {
      obj.currentChallenge = Math.round(message.currentChallenge);
    }
    if (message.currentState?.length) {
      obj.currentState = message.currentState.map((e) => Math.round(e));
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<CheckGoalResponse>, I>>(base?: I): CheckGoalResponse {
    return CheckGoalResponse.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<CheckGoalResponse>, I>>(object: I): CheckGoalResponse {
    const message = createBaseCheckGoalResponse();
    message.currentChallenge = object.currentChallenge ?? 0;
    message.currentState = object.currentState?.map((e) => e) || [];
    return message;
  },
};

function createBaseClaimRewardRequest(): ClaimRewardRequest {
  return { enrollmentFilter: undefined };
}

export const ClaimRewardRequest = {
  encode(message: ClaimRewardRequest, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.enrollmentFilter !== undefined) {
      EnrollmentFilter.encode(message.enrollmentFilter, writer.uint32(10).fork()).ldelim();
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ClaimRewardRequest {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseClaimRewardRequest();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.enrollmentFilter = EnrollmentFilter.decode(reader, reader.uint32());
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ClaimRewardRequest {
    return {
      enrollmentFilter: isSet(object.enrollmentFilter) ? EnrollmentFilter.fromJSON(object.enrollmentFilter) : undefined,
    };
  },

  toJSON(message: ClaimRewardRequest): unknown {
    const obj: any = {};
    if (message.enrollmentFilter !== undefined) {
      obj.enrollmentFilter = EnrollmentFilter.toJSON(message.enrollmentFilter);
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ClaimRewardRequest>, I>>(base?: I): ClaimRewardRequest {
    return ClaimRewardRequest.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ClaimRewardRequest>, I>>(object: I): ClaimRewardRequest {
    const message = createBaseClaimRewardRequest();
    message.enrollmentFilter = (object.enrollmentFilter !== undefined && object.enrollmentFilter !== null)
      ? EnrollmentFilter.fromPartial(object.enrollmentFilter)
      : undefined;
    return message;
  },
};

function createBaseClaimRewardResponse(): ClaimRewardResponse {
  return { reward: "" };
}

export const ClaimRewardResponse = {
  encode(message: ClaimRewardResponse, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.reward !== "") {
      writer.uint32(10).string(message.reward);
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ClaimRewardResponse {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseClaimRewardResponse();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.reward = reader.string();
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ClaimRewardResponse {
    return { reward: isSet(object.reward) ? globalThis.String(object.reward) : "" };
  },

  toJSON(message: ClaimRewardResponse): unknown {
    const obj: any = {};
    if (message.reward !== "") {
      obj.reward = message.reward;
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ClaimRewardResponse>, I>>(base?: I): ClaimRewardResponse {
    return ClaimRewardResponse.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ClaimRewardResponse>, I>>(object: I): ClaimRewardResponse {
    const message = createBaseClaimRewardResponse();
    message.reward = object.reward ?? "";
    return message;
  },
};

function createBaseContestListRequest(): ContestListRequest {
  return { author: "", limit: 0, offset: 0 };
}

export const ContestListRequest = {
  encode(message: ContestListRequest, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    if (message.author !== "") {
      writer.uint32(10).string(message.author);
    }
    if (message.limit !== 0) {
      writer.uint32(16).uint32(message.limit);
    }
    if (message.offset !== 0) {
      writer.uint32(24).uint32(message.offset);
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ContestListRequest {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseContestListRequest();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.author = reader.string();
          continue;
        case 2:
          if (tag !== 16) {
            break;
          }

          message.limit = reader.uint32();
          continue;
        case 3:
          if (tag !== 24) {
            break;
          }

          message.offset = reader.uint32();
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ContestListRequest {
    return {
      author: isSet(object.author) ? globalThis.String(object.author) : "",
      limit: isSet(object.limit) ? globalThis.Number(object.limit) : 0,
      offset: isSet(object.offset) ? globalThis.Number(object.offset) : 0,
    };
  },

  toJSON(message: ContestListRequest): unknown {
    const obj: any = {};
    if (message.author !== "") {
      obj.author = message.author;
    }
    if (message.limit !== 0) {
      obj.limit = Math.round(message.limit);
    }
    if (message.offset !== 0) {
      obj.offset = Math.round(message.offset);
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ContestListRequest>, I>>(base?: I): ContestListRequest {
    return ContestListRequest.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ContestListRequest>, I>>(object: I): ContestListRequest {
    const message = createBaseContestListRequest();
    message.author = object.author ?? "";
    message.limit = object.limit ?? 0;
    message.offset = object.offset ?? 0;
    return message;
  },
};

function createBaseContestListResponse(): ContestListResponse {
  return { contests: [] };
}

export const ContestListResponse = {
  encode(message: ContestListResponse, writer: _m0.Writer = _m0.Writer.create()): _m0.Writer {
    for (const v of message.contests) {
      Contest.encode(v!, writer.uint32(10).fork()).ldelim();
    }
    return writer;
  },

  decode(input: _m0.Reader | Uint8Array, length?: number): ContestListResponse {
    const reader = input instanceof _m0.Reader ? input : _m0.Reader.create(input);
    let end = length === undefined ? reader.len : reader.pos + length;
    const message = createBaseContestListResponse();
    while (reader.pos < end) {
      const tag = reader.uint32();
      switch (tag >>> 3) {
        case 1:
          if (tag !== 10) {
            break;
          }

          message.contests.push(Contest.decode(reader, reader.uint32()));
          continue;
      }
      if ((tag & 7) === 4 || tag === 0) {
        break;
      }
      reader.skipType(tag & 7);
    }
    return message;
  },

  fromJSON(object: any): ContestListResponse {
    return {
      contests: globalThis.Array.isArray(object?.contests) ? object.contests.map((e: any) => Contest.fromJSON(e)) : [],
    };
  },

  toJSON(message: ContestListResponse): unknown {
    const obj: any = {};
    if (message.contests?.length) {
      obj.contests = message.contests.map((e) => Contest.toJSON(e));
    }
    return obj;
  },

  create<I extends Exact<DeepPartial<ContestListResponse>, I>>(base?: I): ContestListResponse {
    return ContestListResponse.fromPartial(base ?? ({} as any));
  },
  fromPartial<I extends Exact<DeepPartial<ContestListResponse>, I>>(object: I): ContestListResponse {
    const message = createBaseContestListResponse();
    message.contests = object.contests?.map((e) => Contest.fromPartial(e)) || [];
    return message;
  },
};

type Builtin = Date | Function | Uint8Array | string | number | boolean | undefined;

export type DeepPartial<T> = T extends Builtin ? T
  : T extends Long ? string | number | Long : T extends globalThis.Array<infer U> ? globalThis.Array<DeepPartial<U>>
  : T extends ReadonlyArray<infer U> ? ReadonlyArray<DeepPartial<U>>
  : T extends { $case: string } ? { [K in keyof Omit<T, "$case">]?: DeepPartial<T[K]> } & { $case: T["$case"] }
  : T extends {} ? { [K in keyof T]?: DeepPartial<T[K]> }
  : Partial<T>;

type KeysOfUnion<T> = T extends T ? keyof T : never;
export type Exact<P, I extends P> = P extends Builtin ? P
  : P & { [K in keyof P]: Exact<P[K], I[K]> } & { [K in Exclude<keyof I, KeysOfUnion<P>>]: never };

if (_m0.util.Long !== Long) {
  _m0.util.Long = Long as any;
  _m0.configure();
}

function isSet(value: any): boolean {
  return value !== null && value !== undefined;
}
