<?php

declare(strict_types=1);

namespace App\Endpoint\Centrifugo\Handler;

use App\Service\SheetService;
use RoadRunner\Centrifugo\Request\Subscribe;
use RoadRunner\Centrifugo\Payload\SubscribeResponse;
use RoadRunner\Centrifugo\Request\RequestInterface;
use Spiral\RoadRunnerBridge\Centrifugo\ServiceInterface;

final class SubscribeHandler implements ServiceInterface
{
    public function __construct(private readonly SheetService $sheetService) {
    }

    /**
     * @param Subscribe $request
     */
    public function handle(RequestInterface $request): void
    {
        try {
            if (!$this->authorizeTopic($request)) {
                $request->error(1001, "Forbidden");
                return;
            }

            $request->respond(
                new SubscribeResponse()
            );
        } catch (\Throwable $e) {
            $request->error($e->getCode(), $e->getMessage());
        }
    }

    private function authorizeTopic(Subscribe $request): bool
    {
        $channel = $request->channel;
        $authToken = $request->getData()["authToken"] ?? "";
        if ($authToken === "") {
            return false;
        }
        $parts = explode(":", $channel, 2);
        if (count($parts) !== 2) {
            return false;
        }
        if ($parts[0] !== "sheets") {
            return false;
        }
        $sheetId = $parts[1];

        if (!$this->sheetService->exists($sheetId)) {
            return false;
        }

        return $this->sheetService->can_read($sheetId, $authToken);
    }
}
