<?php

use Spiral\Auth\Transport\CookieTransport;
use Spiral\Auth\Transport\HeaderTransport;
use Spiral\Core\Container\Autowire;

return [
    'transports' => [
        'header' => new HeaderTransport(header: 'X-Auth-Token'),
        'cookies' => new CookieTransport(cookie: 'auth-token'),
    ],
    'storages' => [
        'cache' => new Autowire(\App\Auth\Storage\CacheTokenStorage::class),
    ],
    'defaultTransport' => env('AUTH_TOKEN_TRANSPORT', 'cookies'),
    'defaultStorage' => env('AUTH_TOKEN_STORAGE', 'cache'),
];
