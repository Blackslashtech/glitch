<?php

namespace App\Service;

use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;
use Psr\SimpleCache\CacheInterface;
use Ramsey\Uuid\Uuid;
use Spiral\Cache\CacheStorageProviderInterface;
use Spiral\Boot\DirectoriesInterface;
use Spiral\Files\FilesInterface;
use Spiral\Prototype\Annotation\Prototyped;


#[Prototyped(property: 'sheetService')]
final class SheetService
{

    private readonly CacheInterface $sheetsStorage;
    private readonly CacheInterface $userData;

    public function __construct(private readonly DirectoriesInterface $dirs,
                                private readonly FilesInterface       $files,
                                CacheStorageProviderInterface         $provider,
    )
    {
        $this->sheetsStorage = $provider->storage('sheets');
        $this->userData = $provider->storage("user-data");
    }

    private const READ_EXT = ".read";
    private const WRITE_EXT = ".modify";

    private function has_access(string $tokenPath, string $token): bool
    {
        if (!file_exists($tokenPath)) {
            return false;
        }

        $cnt = file_get_contents($tokenPath);
        return $cnt == $token;
    }

    public function modifySheet(string $sid, string $cell, string $value): array
    {
        $spreadsheet = IOFactory::load($this->pathTo($sid));
        $worksheet = $spreadsheet->getActiveSheet();
        $c = $worksheet->getCell($cell);
        $c->setValue($value);

        $writer = new Xlsx($spreadsheet);
        $writer->save($this->pathTo($sid));

        return $this->readWorksheet($worksheet);
    }

    public function readSheet(string $sid): array
    {
        $spreadsheet = IOFactory::load($this->pathTo($sid));
        $worksheet = $spreadsheet->getActiveSheet();
        return $this->readWorksheet($worksheet);
    }

    public function createSheet(string $userId, string $title, string $uploadedPath): array
    {
        $sid = Uuid::uuid4()->toString();
        $readToken = Uuid::uuid4()->getHex()->toString();
        $modifyToken = Uuid::uuid4()->getHex()->toString();

        $this->sheetsStorage->set($sid, [
            "readToken" => $readToken,
            "modifyToken" => $modifyToken,
            "title" => $title,
        ]);

        if ($this->files->write($this->guard_path($sid, self::WRITE_EXT), $modifyToken) === false) {
            return [];
        }
        if ($this->files->write($this->guard_path($sid, self::READ_EXT), $readToken) === false) {
            return [];
        }

        $userSheets = $this->userData->get($userId) ?? [];
        $userSheets[] = $sid;

        $this->userData->set($userId, $userSheets);
        $this->files->move($uploadedPath, $this->pathTo($sid));


        return [
            "sid" => $sid,
            "readToken" => $readToken,
            "modifyToken" => $modifyToken,
            "title" => $title,
        ];
    }


    public function user_sheets(string $userId): array
    {
        $result = [];
        $sheetIds = $this->userData->get($userId) ?? [];
        $sheets = $this->sheetsStorage->getMultiple($sheetIds);
        foreach ($sheets as $sid => $sheet) {
            $result[] = [
                "sid" => $sid,
                "readToken" => $sheet["readToken"] ?? "",
                "modifyToken" => $sheet["modifyToken"] ?? "",
                "title" => $sheet["title"] ?? "",
            ];
        }

        return $result;
    }

    public function pathTo(string $sid): string
    {
        $filesDir = $this->dirs->get("user-files");
        return "$filesDir$sid";
    }

    public function exists(string $sid): bool
    {
        $filesDir = $this->dirs->get("user-files");
        $fpath = "$filesDir$sid";
        return file_exists($fpath);
    }

    public function can_read(string $sid, string $token): bool
    {
        return $this->has_access($this->guard_path($sid, self::READ_EXT), $token);
    }

    private function guard_path(string $sid, string $ext): string
    {
        $aclsDir = $this->dirs->get("acls");

        return "$aclsDir$sid$ext";
    }

    public function can_write(string $sid, string $token): bool
    {
        return $this->has_access($this->guard_path($sid, self::WRITE_EXT), $token);
    }

    /**
     * @param \PhpOffice\PhpSpreadsheet\Worksheet\Worksheet $worksheet
     * @return array
     */
    public function readWorksheet(\PhpOffice\PhpSpreadsheet\Worksheet\Worksheet $worksheet): array
    {
        $title = $worksheet->getTitle();
        $cells = [];
        foreach ($worksheet->getRowIterator() as $row) {
            $cellIterator = $row->getCellIterator();
            $cellIterator->setIterateOnlyExistingCells(true);
            foreach ($cellIterator as $cell) {
                $col = $cell->getColumn();
                $row = $cell->getRow();
                $val = $cell->getFormattedValue();
                $cells [] = [
                    "row" => $row,
                    "col" => $col,
                    "val" => $val,
                ];
            }
        }
        return [
            "title" => $title,
            "cells" => $cells,
        ];
    }
}
