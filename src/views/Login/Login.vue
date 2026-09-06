<template>
  <div class="body" @keydown.enter="isSign ? handleRegister : handleLogin">
    
    <div class="container">
      <div class="form-section">
        
        <div class="login-form" v-if="!isSign">
          <h2 class="form-subtitle">登录</h2>
          <div class="register-tip">
            <span class="tip-text">没有账号？</span>
            <a href="javascript:;" class="register-link" @click="toSign">注册新账号</a>
          </div>

          <div class="input-item">
            <span class="input-icon">
              <svg class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="200" height="200"><path d="M493.60896 148.70528c91.77088 0 166.44096 75.79648 166.44096 168.96s-74.67008 168.96-166.44096 168.96-166.44096-75.79648-166.44096-168.96S401.83808 148.70528 493.60896 148.70528L493.60896 148.70528zM581.2224 601.00608c122.5728 0 222.28992 101.13024 222.3104 225.44384l0 16.15872c0 4.68992-0.83968 6.0416-3.97312 8.51968-4.05504 3.21536-14.52032 9.33888-38.97344 14.2336-44.68736 8.92928-110.10048 8.92928-179.34336 8.92928l-159.31392 0c-70.73792 0-137.5232 0-181.41184-8.9088-23.51104-4.77184-33.34144-10.67008-37.13024-13.78304-2.4576-2.00704-3.72736-3.31776-3.72736-8.99072l0-16.15872c0-124.3136 99.71712-225.44384 222.26944-225.44384L581.2224 601.00608 581.2224 601.00608zM493.60896 101.888c-117.248 0-212.64384 96.80896-212.64384 215.7568 0 118.94784 95.39584 215.7568 212.64384 215.7568 117.248 0 212.64384-96.78848 212.64384-215.7568C706.2528 198.67648 610.85696 101.888 493.60896 101.888L493.60896 101.888M581.2224 554.20928l-159.31392 0c-148.0704 0-268.4928 122.12224-268.4928 272.24064l0 16.15872c0 78.49984 118.49728 78.49984 268.4928 78.49984l159.31392 0c144.09728 0 268.51328 0 268.51328-78.49984l0-16.15872C849.73568 676.352 729.2928 554.20928 581.2224 554.20928L581.2224 554.20928" fill="#030000"></path></svg>
            </span>
            <input type="text" v-model="loginUser" placeholder="用户名" class="input-field" />
          </div>
          <div class="input-item">
            <span class="input-icon">
              <svg class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="200" height="200"><path d="M712.06912 374.39488 329.80992 374.39488l0-70.144c0-88.28928 77.37344-157.47072 176.3328-158.02368 96.70656 0.512 169.53344 68.1984 169.53344 158.02368l0 35.1232c0 9.66656 8.13056 17.55136 18.20672 17.55136 10.07616 0 18.20672-7.82336 18.20672-17.55136l0-35.1232c0-109.40416-87.87968-192.02048-204.75904-193.08544l-2.33472 0c-118.784 1.06496-211.59936 85.48352-211.59936 193.08544l0 71.9872c-61.58336 8.66304-109.24032 59.392-109.24032 121.09824l0 228.20864c0 67.82976 57.1392 122.90048 127.44704 122.90048l400.4864 0c70.3488 0 127.44704-55.07072 127.44704-122.90048L839.53664 497.33632C839.51616 429.54752 782.31552 374.39488 712.06912 374.39488L712.06912 374.39488 712.06912 374.39488zM803.10272 725.48352c0 48.4352-40.81664 87.77728-91.0336 87.77728L311.6032 813.2608c-50.21696 0-90.97216-39.36256-90.97216-87.77728L220.63104 497.29536c0-48.4352 40.81664-87.73632 90.97216-87.73632l400.4864 0c50.2784 0 91.0336 39.36256 91.0336 87.73632L803.1232 725.48352 803.10272 725.48352zM511.81568 479.72352c-60.2112 0-109.24032 47.22688-109.24032 105.34912 0 52.16256 39.66976 95.29344 91.40224 103.54688-0.04096 0.63488-0.38912 1.10592-0.38912 1.7408l0 52.67456c0 9.728 8.13056 17.6128 18.20672 17.6128s18.20672-7.8848 18.20672-17.6128L530.00192 690.3808c0-0.65536-0.32768-1.10592-0.38912-1.7408 51.75296-8.25344 91.40224-51.38432 91.40224-103.54688C621.056 526.97088 572.06784 479.72352 511.81568 479.72352L511.81568 479.72352 511.81568 479.72352zM511.81568 655.31904c-40.1408 0-72.82688-31.55968-72.82688-70.18496 0-38.74816 32.72704-70.18496 72.82688-70.18496 40.09984 0 72.72448 31.51872 72.72448 70.18496C584.64256 623.77984 551.95648 655.31904 511.81568 655.31904L511.81568 655.31904 511.81568 655.31904z" fill="#030000"></path></svg>
            </span>
            <input :type="showPassword ? 'text' : 'password'" v-model="loginPassword" placeholder="密码" class="input-field" />
            <span class="password-eye" @click="togglePassword">
              <svg v-if="showPassword" t="1775282763791" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1988" width="200" height="200"><path d="M512 284.19072c72.35072 0 160.18944 36.57728 247.33184 102.9888 64.68608 49.30048 108.30848 99.36896 126.17728 125.17888-17.8432 25.5232-62.29504 75.64288-129.3312 125.63456-88.04864 65.664-174.76608 101.82144-244.17792 101.82144-70.528 0-157.68064-36.58752-245.4016-103.02464-65.13664-49.3312-109.26592-99.0976-127.67744-125.05088 18.13504-25.984 61.57312-75.648 125.75232-124.55936C351.81056 320.76288 439.64928 284.19072 512 284.19072m0-70.87616c-220.32896 0-450.56 250.59328-450.56 298.68544s235.18208 298.68544 450.56 298.68544c210.42688 0 450.56-245.5296 450.56-298.68544 0-48.09216-230.23104-298.68544-450.56-298.68544z" fill="#666666" p-id="1989"></path><path d="M512 446.18752c36.28544 0 65.81248 29.52192 65.81248 65.81248s-29.52704 65.81248-65.81248 65.81248S446.18752 548.29056 446.18752 512 475.71456 446.18752 512 446.18752m0-70.87616c-75.48928 0-136.68864 61.19424-136.68864 136.68864S436.51072 648.68864 512 648.68864s136.68864-61.19424 136.68864-136.68864S587.48928 375.31136 512 375.31136z" fill="#666666" p-id="1990"></path></svg>
              <svg v-else  t="1775282053179" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1656" width="200" height="200"><path d="M926.03392 339.87072c-9.86624 0-19.16928 4.14208-26.17856 11.0848-14.09024 13.94688-39.44448 30.94016-79.85664 47.27808-79.86176 32.28672-192.12288 50.80064-307.9936 50.80064s-228.13696-18.51392-307.9936-50.80064c-40.41216-16.33792-65.7664-33.3312-79.85664-47.27808-7.0144-6.94272-16.31232-11.07968-26.17856-11.07968-33.05472 0-48.9984 40.35584-24.9856 63.07328 72.832 68.89472 241.9712 117.1712 439.01952 117.1712s366.18752-48.2816 439.01952-117.1712c24.00256-22.72256 8.05376-63.0784-24.99584-63.0784z" fill="#666666" p-id="1657"></path><path d="M353.83808 642.41152l22.92224-130.00192a35.54816 35.54816 0 0 1 70.00064 12.3392l-22.92224 130.00192a35.53792 35.53792 0 1 1-70.00064-12.3392zM610.31424 654.75584l-22.92224-130.00192a35.5328 35.5328 0 0 1 28.83072-41.16992 35.5328 35.5328 0 0 1 41.16992 28.83072l22.92224 130.00192a35.54816 35.54816 0 0 1-70.00064 12.3392zM878.7968 589.37856l-93.34272-93.34272a35.53792 35.53792 0 1 1 50.26304-50.26304l93.34272 93.34272a35.53792 35.53792 0 1 1-50.26304 50.26304zM105.09824 539.11552l93.34272-93.34272a35.53792 35.53792 0 1 1 50.26304 50.26304l-93.34272 93.34272a35.53792 35.53792 0 1 1-50.26304-50.26304z" fill="#666666" p-id="1658"></path></svg>
  
             </span>
          </div>

          <div class="form-options">
            <label class="remember-me">
              <input type="checkbox" v-model="rememberMe" />
              <span>记住账号</span>
            </label>
            <a href="javascript:;" class="forgot-link">忘记账号？</a>
          </div>

          <button class="submit-btn" @click="handleLogin">登录</button>

          <div class="other-login">
            <a href="javascript:;" class="other-link">使用微信扫码登录</a>
            <span class="divider">|</span>
            <a href="javascript:;" class="other-link">使用手机号登录</a>
          </div>
        </div>

        <div class="login-form" v-else>
          <h2 class="form-subtitle">注册</h2>
          <div class="register-tip">
            <span class="tip-text">已有账号？</span>
            <a href="javascript:;" class="register-link" @click="toLogin">去登录</a>
          </div>

          <div class="input-item">
            <span class="input-icon">
              <svg class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="200" height="200"><path d="M493.60896 148.70528c91.77088 0 166.44096 75.79648 166.44096 168.96s-74.67008 168.96-166.44096 168.96-166.44096-75.79648-166.44096-168.96S401.83808 148.70528 493.60896 148.70528L493.60896 148.70528zM581.2224 601.00608c122.5728 0 222.28992 101.13024 222.3104 225.44384l0 16.15872c0 4.68992-0.83968 6.0416-3.97312 8.51968-4.05504 3.21536-14.52032 9.33888-38.97344 14.2336-44.68736 8.92928-110.10048 8.92928-179.34336 8.92928l-159.31392 0c-70.73792 0-137.5232 0-181.41184-8.9088-23.51104-4.77184-33.34144-10.67008-37.13024-13.78304-2.4576-2.00704-3.72736-3.31776-3.72736-8.99072l0-16.15872c0-124.3136 99.71712-225.44384 222.26944-225.44384L581.2224 601.00608 581.2224 601.00608zM493.60896 101.888c-117.248 0-212.64384 96.80896-212.64384 215.7568 0 118.94784 95.39584 215.7568 212.64384 215.7568 117.248 0 212.64384-96.78848 212.64384-215.7568C706.2528 198.67648 610.85696 101.888 493.60896 101.888L493.60896 101.888M581.2224 554.20928l-159.31392 0c-148.0704 0-268.4928 122.12224-268.4928 272.24064l0 16.15872c0 78.49984 118.49728 78.49984 268.4928 78.49984l159.31392 0c144.09728 0 268.51328 0 268.51328-78.49984l0-16.15872C849.73568 676.352 729.2928 554.20928 581.2224 554.20928L581.2224 554.20928" fill="#030000"></path></svg>
            </span>
            <input type="text" v-model="signUser" placeholder="设置用户名" class="input-field" />
          </div>
          <div class="input-item">
            <span class="input-icon">
              <svg class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="200" height="200"><path d="M712.06912 374.39488 329.80992 374.39488l0-70.144c0-88.28928 77.37344-157.47072 176.3328-158.02368 96.70656 0.512 169.53344 68.1984 169.53344 158.02368l0 35.1232c0 9.66656 8.13056 17.55136 18.20672 17.55136 10.07616 0 18.20672-7.82336 18.20672-17.55136l0-35.1232c0-109.40416-87.87968-192.02048-204.75904-193.08544l-2.33472 0c-118.784 1.06496-211.59936 85.48352-211.59936 193.08544l0 71.9872c-61.58336 8.66304-109.24032 59.392-109.24032 121.09824l0 228.20864c0 67.82976 57.1392 122.90048 127.44704 122.90048l400.4864 0c70.3488 0 127.44704-55.07072 127.44704-122.90048L839.53664 497.33632C839.51616 429.54752 782.31552 374.39488 712.06912 374.39488L712.06912 374.39488 712.06912 374.39488zM803.10272 725.48352c0 48.4352-40.81664 87.77728-91.0336 87.77728L311.6032 813.2608c-50.21696 0-90.97216-39.36256-90.97216-87.77728L220.63104 497.29536c0-48.4352 40.81664-87.73632 90.97216-87.73632l400.4864 0c50.2784 0 91.0336 39.36256 91.0336 87.73632L803.1232 725.48352 803.10272 725.48352zM511.81568 479.72352c-60.2112 0-109.24032 47.22688-109.24032 105.34912 0 52.16256 39.66976 95.29344 91.40224 103.54688-0.04096 0.63488-0.38912 1.10592-0.38912 1.7408l0 52.67456c0 9.728 8.13056 17.6128 18.20672 17.6128s18.20672-7.8848 18.20672-17.6128L530.00192 690.3808c0-0.65536-0.32768-1.10592-0.38912-1.7408 51.75296-8.25344 91.40224-51.38432 91.40224-103.54688C621.056 526.97088 572.06784 479.72352 511.81568 479.72352L511.81568 479.72352 511.81568 479.72352zM511.81568 655.31904c-40.1408 0-72.82688-31.55968-72.82688-70.18496 0-38.74816 32.72704-70.18496 72.82688-70.18496 40.09984 0 72.72448 31.51872 72.72448 70.18496C584.64256 623.77984 551.95648 655.31904 511.81568 655.31904L511.81568 655.31904 511.81568 655.31904z" fill="#030000"></path></svg>
            </span>
            <input :type="showPassword ? 'text' : 'password'" v-model="signPassword" placeholder="设置密码" class="input-field" />
            <span class="password-eye" @click="togglePassword">
              <svg v-if="showPassword" t="1775282763791" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1988" width="200" height="200"><path d="M512 284.19072c72.35072 0 160.18944 36.57728 247.33184 102.9888 64.68608 49.30048 108.30848 99.36896 126.17728 125.17888-17.8432 25.5232-62.29504 75.64288-129.3312 125.63456-88.04864 65.664-174.76608 101.82144-244.17792 101.82144-70.528 0-157.68064-36.58752-245.4016-103.02464-65.13664-49.3312-109.26592-99.0976-127.67744-125.05088 18.13504-25.984 61.57312-75.648 125.75232-124.55936C351.81056 320.76288 439.64928 284.19072 512 284.19072m0-70.87616c-220.32896 0-450.56 250.59328-450.56 298.68544s235.18208 298.68544 450.56 298.68544c210.42688 0 450.56-245.5296 450.56-298.68544 0-48.09216-230.23104-298.68544-450.56-298.68544z" fill="#666666" p-id="1989"></path><path d="M512 446.18752c36.28544 0 65.81248 29.52192 65.81248 65.81248s-29.52704 65.81248-65.81248 65.81248S446.18752 548.29056 446.18752 512 475.71456 446.18752 512 446.18752m0-70.87616c-75.48928 0-136.68864 61.19424-136.68864 136.68864S436.51072 648.68864 512 648.68864s136.68864-61.19424 136.68864-136.68864S587.48928 375.31136 512 375.31136z" fill="#666666" p-id="1990"></path></svg>
              <svg v-else  t="1775282053179" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="1656" width="200" height="200"><path d="M926.03392 339.87072c-9.86624 0-19.16928 4.14208-26.17856 11.0848-14.09024 13.94688-39.44448 30.94016-79.85664 47.27808-79.86176 32.28672-192.12288 50.80064-307.9936 50.80064s-228.13696-18.51392-307.9936-50.80064c-40.41216-16.33792-65.7664-33.3312-79.85664-47.27808-7.0144-6.94272-16.31232-11.07968-26.17856-11.07968-33.05472 0-48.9984 40.35584-24.9856 63.07328 72.832 68.89472 241.9712 117.1712 439.01952 117.1712s366.18752-48.2816 439.01952-117.1712c24.00256-22.72256 8.05376-63.0784-24.99584-63.0784z" fill="#666666" p-id="1657"></path><path d="M353.83808 642.41152l22.92224-130.00192a35.54816 35.54816 0 0 1 70.00064 12.3392l-22.92224 130.00192a35.53792 35.53792 0 1 1-70.00064-12.3392zM610.31424 654.75584l-22.92224-130.00192a35.5328 35.5328 0 0 1 28.83072-41.16992 35.5328 35.5328 0 0 1 41.16992 28.83072l22.92224 130.00192a35.54816 35.54816 0 0 1-70.00064 12.3392zM878.7968 589.37856l-93.34272-93.34272a35.53792 35.53792 0 1 1 50.26304-50.26304l93.34272 93.34272a35.53792 35.53792 0 1 1-50.26304 50.26304zM105.09824 539.11552l93.34272-93.34272a35.53792 35.53792 0 1 1 50.26304 50.26304l-93.34272 93.34272a35.53792 35.53792 0 1 1-50.26304-50.26304z" fill="#666666" p-id="1658"></path></svg>
  
            </span>
          </div>

          <div class="input-item">
            <span class="input-icon">
              <svg class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" width="200" height="200"><path d="M712.06912 374.39488 329.80992 374.39488l0-70.144c0-88.28928 77.37344-157.47072 176.3328-158.02368 96.70656 0.512 169.53344 68.1984 169.53344 158.02368l0 35.1232c0 9.66656 8.13056 17.55136 18.20672 17.55136 10.07616 0 18.20672-7.82336 18.20672-17.55136l0-35.1232c0-109.40416-87.87968-192.02048-204.75904-193.08544l-2.33472 0c-118.784 1.06496-211.59936 85.48352-211.59936 193.08544l0 71.9872c-61.58336 8.66304-109.24032 59.392-109.24032 121.09824l0 228.20864c0 67.82976 57.1392 122.90048 127.44704 122.90048l400.4864 0c70.3488 0 127.44704-55.07072 127.44704-122.90048L839.53664 497.33632C839.51616 429.54752 782.31552 374.39488 712.06912 374.39488L712.06912 374.39488 712.06912 374.39488zM803.10272 725.48352c0 48.4352-40.81664 87.77728-91.0336 87.77728L311.6032 813.2608c-50.21696 0-90.97216-39.36256-90.97216-87.77728L220.63104 497.29536c0-48.4352 40.81664-87.73632 90.97216-87.73632l400.4864 0c50.2784 0 91.0336 39.36256 91.0336 87.73632L803.1232 725.48352 803.10272 725.48352zM511.81568 479.72352c-60.2112 0-109.24032 47.22688-109.24032 105.34912 0 52.16256 39.66976 95.29344 91.40224 103.54688-0.04096 0.63488-0.38912 1.10592-0.38912 1.7408l0 52.67456c0 9.728 8.13056 17.6128 18.20672 17.6128s18.20672-7.8848 18.20672-17.6128L530.00192 690.3808c0-0.65536-0.32768-1.10592-0.38912-1.7408 51.75296-8.25344 91.40224-51.38432 91.40224-103.54688C621.056 526.97088 572.06784 479.72352 511.81568 479.72352L511.81568 479.72352 511.81568 479.72352zM511.81568 655.31904c-40.1408 0-72.82688-31.55968-72.82688-70.18496 0-38.74816 32.72704-70.18496 72.82688-70.18496 40.09984 0 72.72448 31.51872 72.72448 70.18496C584.64256 623.77984 551.95648 655.31904 511.81568 655.31904L511.81568 655.31904 511.81568 655.31904z" fill="#030000"></path></svg>
            </span>
            <input :type="showPassword ? 'text' : 'password'" v-model="confirmPassword" placeholder="请再次确认密码" class="input-field" />
          </div>

          <div class="form-options" style="justify-content: flex-start; margin-top: -8px;">
            <label class="remember-me" style="font-size: 13px;">
              <input type="checkbox" v-model="agreeTos" />
              <span>我已阅读并同意 <a href="javascript:;" class="forgot-link">《用户服务协议》</a> 与 <a href="javascript:;" class="forgot-link">《隐私政策》</a></span>
            </label>
          </div>

          <button class="submit-btn" @click="handleRegister">注册</button>

          <div class="other-login">
            <a href="javascript:;" class="other-link">使用微信扫码登录</a>
            <span class="divider">|</span>
            <a href="javascript:;" class="other-link">使用手机号登录</a>
          </div>
        </div>

        <div class="enterprise-entry">
          <div class="entry-divider">
            <span>我是企业HR/面试官</span>
          </div>
          <button class="switch-b-btn" @click="goToBEnd">
            切换至企业管理后台 ➔
          </button>
        </div>

      </div>

      <div class="bg-decoration">
        <div class="bg-shape primary-btn">Primary</div>
        <div class="bg-shape secondary-btn">Secondary</div>
        <div class="bg-shape t-logo">T</div>
        <div class="bg-circle circle-blue"></div>
        <div class="bg-circle circle-green"></div>
        <div class="bg-circle circle-white"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import axios from 'axios';

const router = useRouter();
const userStore = useUserStore();

const isSign = ref(false);
const rememberMe = ref(false);
const showPassword = ref(false);

const loginUser = ref("");
const loginPassword = ref("");
const signUser = ref("");
const signPassword = ref("");
const confirmPassword = ref(""); 
const agreeTos = ref(false);   

function toSign() { isSign.value = true; }
function toLogin() { isSign.value = false; }
function togglePassword() { showPassword.value = !showPassword.value; }

// ================== 新增：跳往 B 端的函数 ==================
const goToBEnd = () => {
  // 修改为你跑 B 端项目的实际端口 (比如 5174)
  window.location.href = 'http://localhost:5174/login'; 
};

// 登录逻辑
const handleLogin = async () => {
  if (!loginUser.value || !loginPassword.value) {
    alert("请输入用户名和密码！");
    return;
  }
  try {
    const response = await axios.post('http://127.0.0.1:8001/api/auth/login', {
      username: loginUser.value,
      password: loginPassword.value
    });
    const token = response.data.token;
    if (token) {
      localStorage.setItem('token', token);
      localStorage.setItem('username', response.data.username);
      localStorage.setItem('userId', response.data.user_id);
      localStorage.setItem('isLogin', 'true');
      userStore.userInfo.username = response.data.username;
      userStore.login();
      router.push('/');
    } else {
      alert("登录失败：未获取到通行证");
    }
  } catch (error) {
    const errorMsg = error.response?.data?.detail || "登录失败，请检查账号密码！";
    alert(errorMsg);
  }
};

// 注册逻辑
const handleRegister = async () => {
if (!signUser.value || !signPassword.value || !confirmPassword.value) {
    alert("请完整填写注册信息！");
    return;
  }
  if (signPassword.value !== confirmPassword.value) {
    alert("两次输入的密码不一致，请重新输入！");
    return;
  }
  if (!agreeTos.value) {
    alert("请先阅读并勾选同意《用户服务协议》与《隐私政策》！");
    return;
  }
  try {
    const response = await axios.post('http://127.0.0.1:8001/api/auth/register', {
      username: signUser.value,
      password: signPassword.value
    });
    if (response.data.status === 'success') {
      alert("注册成功！请登录");
      loginUser.value = signUser.value;
      toLogin();
    }
  } catch (error) {
    let errorMsg = "注册失败！";
    if (error.response?.status === 422) {
      const details = error.response.data.detail;
      if (Array.isArray(details)) {
        errorMsg = "参数错误：\n" + details.map(d => `${d.loc[d.loc.length-1]}: ${d.msg}`).join('\n');
      }
    } else if (error.response?.data?.detail) {
      errorMsg = error.response.data.detail;
    }
    alert(errorMsg);
  }
};
</script>

<style scoped>
* {
  padding: 0;
  margin: 0;
  box-sizing: border-box;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.body {
  height: 100vh;
  width: 100vw;
  background-image: url(../../assets/images/bg/Login-bg.jpg);
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center center; 
  overflow: hidden;
}

.header {
  display: none; /* 隐藏冲突的顶栏，交给 NavBar 接管 */
}

/* 主容器 */
.container {
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 150px;
}

/* 左侧表单区域 */
.form-section {
  width: 400px;
  z-index: 2;
}

.form-subtitle {
  font-size: 40px;
  font-weight: 600;
  color: #132838;
  margin-bottom: 24px;
}

.register-tip {
  font-size: 14px;
  margin-bottom: 32px;
}
.tip-text { color: #c9cdd4; }
.register-link { color: #2b4c80; text-decoration: none; margin-left: 4px; cursor: pointer; }

/* 输入框样式 */
.input-item {
  position: relative;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  border: 1px solid #e5e6eb;
  border-radius: 4px;
  padding: 0 12px;
  height: 44px;
  background: #ffffff; /* 确保表单背景为白色，防透明穿透 */
}

.input-icon { margin-right: 8px; font-size: 16px; color: #86909c; }
.input-field { flex: 1; border: none; outline: none; font-size: 14px; color: #000; background: transparent; }
.input-field::placeholder { color: #c9cdd4; }
.password-eye { margin-left: 8px; font-size: 16px; color: #86909c; cursor: pointer; }

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 16px 0 24px;
  font-size: 14px;
}
.remember-me { display: flex; align-items: center; color: #86909c; cursor: pointer; }
.remember-me input { margin-right: 6px; }
.forgot-link { color: #0052d9; text-decoration: none; cursor: pointer; }

/* 提交按钮 */
.submit-btn {
  width: 100%; height: 44px; background: #3a7ac4; color: #fff;
  border: none; border-radius: 4px; font-size: 16px; cursor: pointer; transition: background 0.3s;
}
.submit-btn:hover { background: #2168b9; }

/* 其他登录方式 */
.other-login { margin-top: 24px; text-align: center; font-size: 14px; }
.other-link { color: #86909c; text-decoration: none; cursor: pointer; }
.divider { margin: 0 12px; color: #e5e6eb; }

/* ================= 🌟 B 端专属切换区域 ================= */
.enterprise-entry {
  margin-top: 40px;
  padding-top: 10px;
}

.entry-divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #c9cdd4;
  font-size: 12px;
  margin-bottom: 16px;
}
.entry-divider::before, .entry-divider::after {
  content: ''; flex: 1; border-bottom: 1px dashed #e5e6eb;
}
.entry-divider span { padding: 0 10px; }

.switch-b-btn {
  width: 100%;
  padding: 12px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid #c9cdd4;
  border-radius: 8px;
  color: #132838;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}
.switch-b-btn:hover {
  background: #ffffff;
  border-color: #3a7ac4;
  color: #3a7ac4;
}

/* 右侧背景装饰 */
.bg-decoration {
  position: absolute; right: 0; top: 0; width: 60%; height: 100%;
}
.icon { width: 22px; height: 22px; }
</style>