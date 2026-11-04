---
name: nestjs-patterns
description: NestJS 的架構模式，涵蓋 module、controller、provider、DTO 驗證、guard、interceptor、設定，以及正式環境等級的 TypeScript 後端。建置或審查 NestJS 後端（module、provider、DTO 驗證、guard 或 interceptor）時使用。
metadata:
  origin: ECC
---

# NestJS Development Patterns

給模組化 TypeScript 後端的正式環境等級 NestJS 模式。

## When to Activate

- 建置 NestJS 的 API 或服務
- 規劃 module、controller 和 provider 的結構
- 加入 DTO 驗證、guard、interceptor 或 exception filter
- 設定會依環境而異的設定值和資料庫整合
- 測試 NestJS 的單元或 HTTP 端點

## Project Structure

```text
src/
├── app.module.ts
├── main.ts
├── common/
│   ├── filters/
│   ├── guards/
│   ├── interceptors/
│   └── pipes/
├── config/
│   ├── configuration.ts
│   └── validation.ts
├── modules/
│   ├── auth/
│   │   ├── auth.controller.ts
│   │   ├── auth.module.ts
│   │   ├── auth.service.ts
│   │   ├── dto/
│   │   ├── guards/
│   │   └── strategies/
│   └── users/
│       ├── dto/
│       ├── entities/
│       ├── users.controller.ts
│       ├── users.module.ts
│       └── users.service.ts
└── prisma/ or database/
```

- 領域程式碼放在功能 module 裡。
- 橫切的 filter、decorator、guard 和 interceptor 放在 `common/`。
- DTO 放在擁有它們的 module 附近。

## Bootstrap and Global Validation

```ts
async function bootstrap() {
  const app = await NestFactory.create(AppModule, { bufferLogs: true });

  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      transformOptions: { enableImplicitConversion: true },
    }),
  );

  app.useGlobalInterceptors(new ClassSerializerInterceptor(app.get(Reflector)));
  app.useGlobalFilters(new HttpExceptionFilter());

  await app.listen(process.env.PORT ?? 3000);
}
bootstrap();
```

- 公開 API 一律啟用 `whitelist` 和 `forbidNonWhitelisted`。
- 偏好用一個全域的驗證 pipe，不要在每個路由重複驗證設定。

## Modules, Controllers, and Providers

```ts
@Module({
  controllers: [UsersController],
  providers: [UsersService],
  exports: [UsersService],
})
export class UsersModule {}

@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get(':id')
  getById(@Param('id', ParseUUIDPipe) id: string) {
    return this.usersService.getById(id);
  }

  @Post()
  create(@Body() dto: CreateUserDto) {
    return this.usersService.create(dto);
  }
}

@Injectable()
export class UsersService {
  constructor(private readonly usersRepo: UsersRepository) {}

  async create(dto: CreateUserDto) {
    return this.usersRepo.create(dto);
  }
}
```

- Controller 要保持精簡：解析 HTTP 輸入、呼叫 provider、回傳回應 DTO。
- 商業邏輯放在可注入的 service 裡，不要放在 controller。
- 只 export 其他 module 真正需要的 provider。

## DTOs and Validation

```ts
export class CreateUserDto {
  @IsEmail()
  email!: string;

  @IsString()
  @Length(2, 80)
  name!: string;

  @IsOptional()
  @IsEnum(UserRole)
  role?: UserRole;
}
```

- 每個請求 DTO 都用 `class-validator` 驗證。
- 用專用的回應 DTO 或 serializer，不要直接回傳 ORM entity。
- 避免洩漏內部欄位，例如密碼 hash、token 或稽核欄位。

## Auth, Guards, and Request Context

```ts
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('admin')
@Get('admin/report')
getAdminReport(@Req() req: AuthenticatedRequest) {
  return this.reportService.getForUser(req.user.id);
}
```

- 驗證策略和 guard 除非真的是共用的，否則放在各自的 module 裡。
- 粗粒度的存取規則寫在 guard 裡，針對特定資源的授權再交給 service 做。
- 已驗證的請求物件，偏好使用明確的請求型別。

## Exception Filters and Error Shape

```ts
@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const response = host.switchToHttp().getResponse<Response>();
    const request = host.switchToHttp().getRequest<Request>();

    if (exception instanceof HttpException) {
      return response.status(exception.getStatus()).json({
        path: request.url,
        error: exception.getResponse(),
      });
    }

    return response.status(500).json({
      path: request.url,
      error: 'Internal server error',
    });
  }
}
```

- 整個 API 維持同一種錯誤 envelope。
- 預期中的 client 錯誤就丟框架的 exception；意外的失敗在中央統一記錄並包裝。

## Config and Environment Validation

```ts
ConfigModule.forRoot({
  isGlobal: true,
  load: [configuration],
  validate: validateEnv,
});
```

- 在啟動時驗證環境變數，不要等第一個請求進來才惰性驗證。
- 讀取設定要透過有型別的 helper 或 config service。
- 在 config factory 裡區分 dev/staging/prod 的差異，不要在功能程式碼裡到處分支。

## Persistence and Transactions

- 把 repository / ORM 程式碼放在用領域語言溝通的 provider 後面。
- 用 Prisma 或 TypeORM 時，把交易式的工作流程隔離在擁有該工作單元的 service 裡。
- 不要讓 controller 直接協調多步驟的寫入。

## Testing

```ts
describe('UsersController', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleRef = await Test.createTestingModule({
      imports: [UsersModule],
    }).compile();

    app = moduleRef.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({ whitelist: true, transform: true }));
    await app.init();
  });
});
```

- 用 mock 過的相依，單獨對 provider 做單元測試。
- 替 guard、驗證 pipe 和 exception filter 加上請求層級的測試。
- 測試裡要用和正式環境相同的全域 pipe/filter。

## Production Defaults

- 啟用結構化紀錄和請求關聯 id。
- 環境/設定無效時直接終止，不要只啟動一半。
- DB/快取 client 偏好用非同步的 provider 初始化，並搭配明確的健康檢查。
- 背景工作和事件消費者放在自己的 module 裡，不要放在 HTTP controller 裡。
- 公開端點的速率限制、驗證和稽核紀錄都要明確。
