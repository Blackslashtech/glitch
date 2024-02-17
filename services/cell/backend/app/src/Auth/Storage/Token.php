<?php

namespace App\Auth\Storage;

use Spiral\Auth\TokenInterface;

final class Token  implements TokenInterface {
    public function __construct(
        private readonly string $id,
        private readonly array $payload,
        private readonly ?\DateTimeInterface $expiresAt = null
    ) {
    }

    public function getID(): string
    {
        return $this->id;
    }

    public function getExpiresAt(): ?\DateTimeInterface
    {
        return $this->expiresAt;
    }

    public function getPayload(): array
    {
        return $this->payload;
    }

    public function pack(): array
    {
        return [
            'id'        => $this->id,
            'expiresAt' => $this->expiresAt?->getTimestamp(),
            'payload'   => $this->payload,
        ];
    }

    public static function unpack(array $data): Token
    {
        $expiresAt = null;
        if ($data['expiresAt'] !== null) {
            $expiresAt = (new \DateTimeImmutable())->setTimestamp($data['expiresAt']);
        }

        return new Token($data['id'], $data['payload'], $expiresAt);
    }


}
