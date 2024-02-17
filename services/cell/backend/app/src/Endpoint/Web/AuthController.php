<?php

declare(strict_types=1);

namespace App\Endpoint\Web;

use App\Service\UserService;
use Ramsey\Uuid\Uuid;
use Spiral\Auth\AuthContextInterface;
use Spiral\Auth\AuthScope;
use Spiral\Auth\TokenStorageInterface;
use Spiral\Router\Annotation\Route;
use Spiral\Http\Request\InputManager;
use Spiral\Session\SessionScope;

/**
 * Simple home page controller. It renders home page template and also provides
 * an example of exception page.
 */
final class AuthController
{
    public function __construct(
        private readonly UserService           $userService,
        private readonly InputManager          $request,
        private readonly AuthScope             $auth,
        private readonly TokenStorageInterface $tokens)
    {
    }

    #[Route(route: '/api/signup', name: 'signup', methods: ['POST'])]
    public function signup(): array
    {
        $login = $this->request->data("login");
        $password = $this->request->data("password");
        if (empty($login) || empty($password)) {
            return [
                "status" => 422,
                "data" => ["error" => "Login or password is missing"]
            ];
        }

        if ($this->userService->find($login) != null) {
            return [
                "status" => 409,
                "data" => ["error" => "User already exists"]
            ];
        }
        $uid = Uuid::uuid4()->toString();
        $this->userService->create($login, $password, $uid);


        $token = $this->tokens->create(["uid" => $uid, "uname" => $login]);
        $this->auth->start($token);

        return [
            "status" => 200,
            "data" => ["uid" => $uid, "username" => $login],
        ];
    }

    #[Route(route: '/api/signin', name: 'signin', methods: ['POST'])]
    public function signin(): array
    {
        $login = $this->request->data("login");
        $password = $this->request->data("password");
        if (empty($login) || empty($password)) {
            return [
                "status" => 422,
                "data" => ["error" => "Login or password is missing"]
            ];
        }

        $userSaved = $this->userService->find($login);
        $passwordSaved = $userSaved["password"] ?? null;
        if ($passwordSaved !== $password) {
            return [
                "status" => 401,
                "data" => ["error" => "Invalid username or password"]
            ];
        }

        $uid = $userSaved["id"];
        $token = $this->tokens->create(["uid" => $uid, "uname" => $login]);
        $this->auth->start($token);

        return [
            "status" => 200,
            "data" => ["uid" => $uid, "username" => $login],
        ];
    }

    #[Route(route: '/api/logout', name: 'logout', methods: ['POST'])]
    public function logout(): array
    {
        $this->auth->close();
        return [
            "status" => 200,
            "data" => ["message" => "Logged out"]
        ];
    }
}
