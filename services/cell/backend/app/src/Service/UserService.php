<?php

namespace App\Service;

use Psr\SimpleCache\CacheInterface;
use Spiral\Cache\CacheStorageProviderInterface;
use Spiral\Prototype\Annotation\Prototyped;

#[Prototyped(property: 'userService')]
final class UserService
{
    private readonly CacheInterface $cache;

    public function __construct(CacheStorageProviderInterface $provider)
    {
        $this->cache = $provider->storage('users');
    }

    public function find(string $username): array
    {
        return $this->cache->get($username) ?? [];
    }

    public function create(string $username, string $password, string $uid): void
    {
        $payload = [
            "username" => $username,
            "password" => $password,
            "id" => $uid
        ];
        $this->cache->set($username, $payload);
    }

}
