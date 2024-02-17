<?php

namespace App\Auth\Storage;

use DateTime;
use Psr\SimpleCache\CacheInterface;
use Spiral\Auth\Exception\TokenStorageException;
use Spiral\Auth\TokenInterface;
use Spiral\Auth\TokenStorageInterface;
use Spiral\Cache\CacheStorageProviderInterface;

final class CacheTokenStorage implements TokenStorageInterface
{
    private readonly CacheInterface $cache;

    public function __construct(CacheStorageProviderInterface $provider)
    {
        $this->cache = $provider->storage('tokens');
    }

    public function load(string $id): ?TokenInterface
    {
        try {
            $data = $this->cache->get($id);
            if ($data === null) {
                return null;
            }
            return Token::unpack($data);
        } catch (\Throwable $e) {
            throw new TokenStorageException('Unable to load session token', (int)$e->getCode(), $e);
        }
    }

    public function create(array $payload, \DateTimeInterface $expiresAt = null): TokenInterface
    {
        try {
            $key = $this->randomHash(16);
            $expired = $expiresAt?->diff(new DateTime());
            $token = new Token($key, $payload, $expiresAt);
            $this->cache->set($key, $token->pack(), $expired);
            return $token;
        } catch (\Throwable $e) {
            throw new TokenStorageException('Unable to create auth token', (int)$e->getCode(), $e);
        }
    }

    public function delete(TokenInterface $token): void
    {
        try {
            $this->cache->delete($token->getID());
        } catch (\Throwable $e) {
            throw new TokenStorageException('Unable to delete auth token', (int)$e->getCode(), $e);
        }
    }


    private function randomHash(int $length): string
    {
        return \substr(\bin2hex(\random_bytes($length)), 0, $length);
    }
}
