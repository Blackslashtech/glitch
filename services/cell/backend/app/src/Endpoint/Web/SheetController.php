<?php

namespace App\Endpoint\Web;

use App\Service\SheetService;
use PhpOffice\PhpSpreadsheet\IOFactory;
use PhpOffice\PhpSpreadsheet\Spreadsheet;
use PhpOffice\PhpSpreadsheet\Writer\Xlsx;
use Ramsey\Uuid\Uuid;
use Spiral\Auth\AuthScope;
use Spiral\Files\FilesInterface;
use Spiral\Http\Request\InputManager;
use Spiral\Router\Annotation\Route;
use Spiral\Session\SessionScope;

class SheetController
{
    public function __construct(
        private readonly FilesInterface $files,
        private readonly InputManager   $request,
        private readonly SheetService $sheetService,
        private readonly AuthScope $auth,
    )
    {
    }



    #[Route(route: '/api/sheets', name: 'sheets_list', methods: ['GET'])]
    public function sheets()
    {
        $uid = $this->auth->getToken()?->getPayload()["uid"] ?? null;
        if ($uid === null) {
            return [
                "status" => 401,
                "data" => ["error" => "Unauthorized"]
            ];
        }
        return $this->sheetService->user_sheets($uid);
    }

    #[Route(route: '/api/sheets/<sid>', name: 'sheet_get', methods: ['GET'])]
    public function sheet(string $sid): array
    {
        if (empty($sid)) {
            return [
                "status" => 404,
                "data" => ["error" => "Sheet id is missing"]
            ];
        }
        if ($this->sheetService->exists($sid) === false){
            return [
                "status" => 404,
                "data" => ["error" => "Sheet not found"]
            ];
        }

        $token = $this->request->query("token") ?? "";
        if ($this->sheetService->can_read($sid, $token) === false) {
            return [
                "status" => 401,
                "data" => ["error" => "Unauthorized"]
            ];
        }
        return $this->sheetService->readSheet($sid);
    }

    #[Route(route: '/api/sheets/upload', name: 'sheets_upload', methods: ['POST'])]
    public function upload(): array
    {
        $uid = $this->auth->getToken()?->getPayload()["uid"] ?? null;
        if (empty($uid)) {
            return [
                "status" => 401,
                "data" => ["error" => "Unauthorized"]
            ];
        }

        $sheetFile = $this->request->file('sheet');
        if ($sheetFile === null) {
            return [
                "status" => 422,
                "data" => ["error" => "Sheet file is missing"]
            ];
        }
        if ($sheetFile->getError() !== UPLOAD_ERR_OK) {
            return [
                "status" => 422,
                "data" => ["error" => "File upload error"]
            ];
        }
        if ($sheetFile->getSize() > 50 * 1024) {
            return [
                "status" => 422,
                "data" => ["error" => "file is too big"],
            ];
        }

        $tmpFilename = $this->files->tempFilename('xlsx');
        $sheetFile->moveTo($tmpFilename);
        if (mime_content_type($tmpFilename) !== "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") {
            return [
                "status" => 422,
                "data" => ["error" => "file is not xlsx"],
            ];
        }
        try {
            $spreadsheet = IOFactory::load($tmpFilename);
            $worksheet = $spreadsheet->getActiveSheet();
            $title = $worksheet->getTitle();
        } catch (\Exception $e) {
            return [
                "status" => 422,
                "data" => ["error" => "file is not xlsx"],
            ];
        }

        $sheetInfo = $this->sheetService->createSheet($uid, $title, $tmpFilename);
        if (empty($sheetInfo)) {
            return [
                "status" => 500,
                "data" => ["error" => "Internal server error"]
            ];
        }
        return $sheetInfo;
    }

    #[Route(route: '/api/sheets/create', name: 'sheets_create', methods: ['POST'])]
    public function create(): array
    {
        $uid = $this->auth->getToken()?->getPayload()["uid"] ?? null;
        if (empty($uid)) {
            return [
                "status" => 401,
                "data" => ["error" => "Unauthorized"]
            ];
        }
        $title = $this->request->data("title");
        if (empty($title)) {
            return [
                "status" => 422,
                "data" => ["error" => "Title is missing"]
            ];
        }

        $tmpFilename = $this->files->tempFilename('xlsx');
        $spreadsheet = new Spreadsheet();
        $activeWorksheet = $spreadsheet->getActiveSheet();
        $activeWorksheet->setTitle($title, false, false);
        $activeWorksheet->setCellValue('A1', 'Hello from Cell!');

        $writer = new Xlsx($spreadsheet);
        $writer->save($tmpFilename);

        $sheetInfo = $this->sheetService->createSheet($uid, $title, $tmpFilename);
        if (empty($sheetInfo)) {
            return [
                "status" => 500,
                "data" => ["error" => "Internal server error"]
            ];
        }

        return $sheetInfo;
    }

}
