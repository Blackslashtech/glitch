<?php

use Spiral\Cache\Storage\ArrayStorage;
use Spiral\Cache\Storage\FileStorage;

return [
    /**
     * -------------------------------------------------------------------------
     *  Default storage
     * -------------------------------------------------------------------------
     *
     * The key of one of the registered cache storages to use by default.
     */
    'default' => env('CACHE_STORAGE', 'rr-redis'),

    /**
     * -------------------------------------------------------------------------
     *  Aliases
     * -------------------------------------------------------------------------
     *
     * Aliases, if you want to use domain specific storages.
     */
    'aliases' => [
        'user-data' => [
            'storage' => 'rr-redis',
            'prefix' => 'user_data_'
        ],
        'sheets' => [
            'storage' => 'rr-redis',
            'prefix' => 'sheets_'
        ],
        'users' => [
            'storage' => 'rr-redis',
            'prefix' => 'users_'
        ],
        'tokens' => [
            'storage' => 'rr-redis',
            'prefix' => 'tokens_'
        ],
    ],

    /**
     * -------------------------------------------------------------------------
     *  Storages
     * -------------------------------------------------------------------------
     *
     * Here you may define all of the cache "storages" for your application as well as their types.
     */
    'storages' => [
        'rr-redis' => [
            'type' => 'roadrunner',
            'driver' => 'redis',
        ],

        'rr-local' => [
            'type' => 'roadrunner',
            'driver' => 'local',
        ],

        'local' => [
            'type' => 'array',
        ],

        'file' => [
            'type' => 'file',
            'path' => directory('runtime') . 'cache',
        ],
    ],

    /**
     * -------------------------------------------------------------------------
     *  Aliases for storage types
     * -------------------------------------------------------------------------
     */
    'typeAliases' => [
        'array' => ArrayStorage::class,
        'file' => FileStorage::class,
    ],
];
