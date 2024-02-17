<?php

declare(strict_types=1);

namespace App\Endpoint\Centrifugo\Handler;

use App\Service\SheetService;
use RoadRunner\Centrifugo\Payload\ConnectResponse;
use RoadRunner\Centrifugo\Request\Connect;
use RoadRunner\Centrifugo\Request\RequestInterface;
use Spiral\RoadRunnerBridge\Centrifugo\ServiceInterface;

use RoadRunner\Centrifugo\Payload\RPCResponse;
use RoadRunner\Centrifugo\Request\RPC;

final class RPCHandler implements ServiceInterface
{
    public function __construct(private readonly SheetService $sheetService,
                                private readonly \RoadRunner\Centrifugo\CentrifugoApiInterface $api)
    {
    }

    /**
     * @param RPC $request
     */
    public function handle(RequestInterface $request): void
    {
        $result = match ($request->method) {
            'sheets.write' => $this->writeToSheet($request->getData()),
            default => ['error' => 'Not found', 'code' => 404]
        };

        try {
            $request->respond(
                new RPCResponse(
                    data: $result
                )
            );
        } catch (\Throwable $e) {
            $request->error($e->getCode(), $e->getMessage());
        }
    }

    private function writeToSheet(array $data): array
    {

        $sheetId = $data["sheetId"] ?? "";
        if ($sheetId === "") {
            return ['error' => 'Sheet ID is required', 'code' => 400];
        }
        $authToken = $data["authToken"] ?? "";
        $cell = $data["cell"] ?? "";
        $value = $data["value"] ?? "";
        if ($cell === "" || $value === "") {
            return ['error' => 'Cell and value are required', 'code' => 400];
        }

        if (!$this->sheetService->exists($sheetId)) {
            return ['error' => 'Sheet not found', 'code' => 404];
        }

        if (!$this->sheetService->can_write($sheetId, $authToken)) {
            return ['error' => 'Unauthorized', 'code' => 401];
        }

        try {
            $out = $this->sheetService->modifySheet($sheetId, $cell, $value);
            $this->api->publish('sheets:' . $sheetId, json_encode($out));
            return ['success' => true, 'sheet' => $out];
        } catch (\Exception $e) {
            return ['error' => $e->getMessage(), 'code' => 500];
        }
    }
}
