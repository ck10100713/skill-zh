---
name: angular-migration
description: 用混合模式、逐步改寫元件和相依注入更新，把 AngularJS 遷移到 Angular。在升級 AngularJS 應用程式、規劃框架遷移，或現代化老舊的 Angular 程式碼時使用。
---

# Angular 遷移

掌握從 AngularJS 到 Angular 的遷移，包括混合應用程式、元件轉換、相依注入的變化和路由遷移。

## 何時使用這個 Skill

- 把 AngularJS（1.x）應用程式遷移到 Angular（2+）
- 執行 AngularJS/Angular 混合應用程式
- 把 directive 轉成 component
- 現代化相依注入
- 遷移路由系統
- 更新到最新的 Angular 版本
- 實作 Angular 最佳實務

## 遷移策略

### 1. Big Bang（整個重寫）

- 整個 app 用 Angular 重寫
- 平行開發
- 一次切換
- **最適合：** 小型 app、全新專案

### 2. Incremental（混合做法）

- AngularJS 和 Angular 並行執行
- 一個功能一個功能地遷移
- 用 ngUpgrade 做互通
- **最適合：** 大型 app、持續交付

### 3. Vertical Slice

- 完整遷移一個功能
- 新功能用 Angular，舊的維持在 AngularJS
- 逐步取代
- **最適合：** 中型 app、功能界線分明

## 混合 App 設定

```typescript
// main.ts - Bootstrap hybrid app
import { platformBrowserDynamic } from "@angular/platform-browser-dynamic";
import { UpgradeModule } from "@angular/upgrade/static";
import { AppModule } from "./app/app.module";

platformBrowserDynamic()
  .bootstrapModule(AppModule)
  .then((platformRef) => {
    const upgrade = platformRef.injector.get(UpgradeModule);
    // Bootstrap AngularJS
    upgrade.bootstrap(document.body, ["myAngularJSApp"], { strictDi: true });
  });
```

```typescript
// app.module.ts
import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";
import { UpgradeModule } from "@angular/upgrade/static";

@NgModule({
  imports: [BrowserModule, UpgradeModule],
})
export class AppModule {
  constructor(private upgrade: UpgradeModule) {}

  ngDoBootstrap() {
    // Bootstrapped manually in main.ts
  }
}
```

## 元件遷移

### AngularJS Controller → Angular Component

```javascript
// Before: AngularJS controller
angular
  .module("myApp")
  .controller("UserController", function ($scope, UserService) {
    $scope.user = {};

    $scope.loadUser = function (id) {
      UserService.getUser(id).then(function (user) {
        $scope.user = user;
      });
    };

    $scope.saveUser = function () {
      UserService.saveUser($scope.user);
    };
  });
```

```typescript
// After: Angular component
import { Component, OnInit } from "@angular/core";
import { UserService } from "./user.service";

@Component({
  selector: "app-user",
  template: `
    <div>
      <h2>{{ user.name }}</h2>
      <button (click)="saveUser()">Save</button>
    </div>
  `,
})
export class UserComponent implements OnInit {
  user: any = {};

  constructor(private userService: UserService) {}

  ngOnInit() {
    this.loadUser(1);
  }

  loadUser(id: number) {
    this.userService.getUser(id).subscribe((user) => {
      this.user = user;
    });
  }

  saveUser() {
    this.userService.saveUser(this.user);
  }
}
```

### AngularJS Directive → Angular Component

```javascript
// Before: AngularJS directive
angular.module("myApp").directive("userCard", function () {
  return {
    restrict: "E",
    scope: {
      user: "=",
      onDelete: "&",
    },
    template: `
      <div class="card">
        <h3>{{ user.name }}</h3>
        <button ng-click="onDelete()">Delete</button>
      </div>
    `,
  };
});
```

```typescript
// After: Angular component
import { Component, Input, Output, EventEmitter } from "@angular/core";

@Component({
  selector: "app-user-card",
  template: `
    <div class="card">
      <h3>{{ user.name }}</h3>
      <button (click)="delete.emit()">Delete</button>
    </div>
  `,
})
export class UserCardComponent {
  @Input() user: any;
  @Output() delete = new EventEmitter<void>();
}

// Usage: <app-user-card [user]="user" (delete)="handleDelete()"></app-user-card>
```

## Service 遷移

```javascript
// Before: AngularJS service
angular.module("myApp").factory("UserService", function ($http) {
  return {
    getUser: function (id) {
      return $http.get("/api/users/" + id);
    },
    saveUser: function (user) {
      return $http.post("/api/users", user);
    },
  };
});
```

```typescript
// After: Angular service
import { Injectable } from "@angular/core";
import { HttpClient } from "@angular/common/http";
import { Observable } from "rxjs";

@Injectable({
  providedIn: "root",
})
export class UserService {
  constructor(private http: HttpClient) {}

  getUser(id: number): Observable<any> {
    return this.http.get(`/api/users/${id}`);
  }

  saveUser(user: any): Observable<any> {
    return this.http.post("/api/users", user);
  }
}
```

## 相依注入的變化

### 降級 Angular → AngularJS

```typescript
// Angular service
import { Injectable } from "@angular/core";

@Injectable({ providedIn: "root" })
export class NewService {
  getData() {
    return "data from Angular";
  }
}

// Make available to AngularJS
import { downgradeInjectable } from "@angular/upgrade/static";

angular.module("myApp").factory("newService", downgradeInjectable(NewService));

// Use in AngularJS
angular.module("myApp").controller("OldController", function (newService) {
  console.log(newService.getData());
});
```

### 升級 AngularJS → Angular

```typescript
// AngularJS service
angular.module('myApp').factory('oldService', function() {
  return {
    getData: function() {
      return 'data from AngularJS';
    }
  };
});

// Make available to Angular
import { InjectionToken } from '@angular/core';

export const OLD_SERVICE = new InjectionToken<any>('oldService');

@NgModule({
  providers: [
    {
      provide: OLD_SERVICE,
      useFactory: (i: any) => i.get('oldService'),
      deps: ['$injector']
    }
  ]
})

// Use in Angular
@Component({...})
export class NewComponent {
  constructor(@Inject(OLD_SERVICE) private oldService: any) {
    console.log(this.oldService.getData());
  }
}
```

## 路由遷移

```javascript
// Before: AngularJS routing
angular.module("myApp").config(function ($routeProvider) {
  $routeProvider
    .when("/users", {
      template: "<user-list></user-list>",
    })
    .when("/users/:id", {
      template: "<user-detail></user-detail>",
    });
});
```

```typescript
// After: Angular routing
import { NgModule } from "@angular/core";
import { RouterModule, Routes } from "@angular/router";

const routes: Routes = [
  { path: "users", component: UserListComponent },
  { path: "users/:id", component: UserDetailComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
```

## 其他模式與範本

更詳細的範本和實作範例放在 `references/details.md`。要看完整的模式庫就讀那個檔案。
