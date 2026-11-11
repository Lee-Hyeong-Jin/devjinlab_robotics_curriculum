---
id: m5-particle-filter-mcl
title: "파티클 필터·몬테카를로 로컬라이제이션"
summary: belief 를 가중치가 붙은 샘플(파티클) 집합으로 표현하면 비선형·다봉 분포도 다룰 수 있다. 샘플링–가중치–재샘플링 세 단계를 구현하고, 이를 지도 위 위치 추정에 쓰는 몬테카를로 로컬라이제이션(MCL)과 ROS 2 의 AMCL 로 연결한다.
objectives:
  - 파티클 필터의 예측(샘플링)·가중치·재샘플링 단계를 설명하고 numpy 로 구현할 수 있다.
  - 계통(systematic) 재샘플링과 유효 파티클 수 N_eff 의 의미를 설명할 수 있다.
  - 칼만 필터와 비교해 MCL 이 전역 위치 추정·납치 로봇 문제에 강한 이유와 비용을 설명할 수 있다.
prerequisites: [m5-kalman-filter-ekf]
difficulty: 3
estimated_minutes: 120
tags: [particle-filter, mcl, amcl, resampling, localization]
activities:
  - id: m5-particle-filter-mcl-reading
    kind: reading
    title: 본문과 Labbe Particle Filters 장 읽기
    estimated_minutes: 45
  - id: m5-particle-filter-mcl-quiz
    kind: quiz
    title: 재샘플링과 파티클 수 퀴즈
    estimated_minutes: 15
  - id: m5-particle-filter-mcl-exercise
    kind: exercise
    title: 랜드마크 기반 2D 파티클 필터 실험
    estimated_minutes: 60
resources:
  - title: "Particle Filter & MCL (Stachniss)"
    url: https://www.youtube.com/watch?v=MsYlueVDLI0
    kind: video
    note: Online Training – Mobile Robotics, Robotics 블록.
  - title: "Kalman and Bayesian Filters in Python (Labbe)"
    url: https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python
    kind: book
    note: Ch. 11 Particle Filters(저장소 판에 따라 장 번호가 다를 수 있다).
  - title: "Probabilistic Robotics (Thrun, Burgard, Fox)"
    url: https://robots.stanford.edu/probabilistic-robotics/
    kind: book
    note: Ch. 4 Nonparametric Filters, Ch. 8 Monte Carlo Localization(KLD 샘플링 포함).
  - title: "Michigan ROB 530 Mobile Robotics"
    url: https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public
    kind: course
    note: 로컬라이제이션 HW 로 연습량 보강(선택).
---

# 파티클 필터·몬테카를로 로컬라이제이션

칼만 필터는 belief 가 봉우리 하나인 가우시안이라고 가정한다. 하지만 똑같이 생긴 복도가 두 개인
건물에서 로봇이 켜지면 "A 복도 또는 B 복도"라는 **두 봉우리** 분포가 필요하다. 파티클 필터는
분포의 모양을 가정하지 않고, 수백~수천 개의 가설(파티클)을 직접 시뮬레이션한다. 지도 위 위치
추정에 쓰면 몬테카를로 로컬라이제이션(MCL)이고, Nav2 의 `nav2_amcl` 이 그 구현이다.

## 개념

### 세 단계

1. **예측(샘플링):** 각 파티클을 모션 모델로 움직이되, 노이즈를 **각자 따로** 뽑아 더한다.
   파티클 구름이 퍼지면서 모션 불확실성을 표현한다.
2. **가중치:** 각 파티클 위치에서 "이 자리라면 지금 관측이 나올 확률" $p(z \mid x^{[i]})$ 를
   계산해 가중치로 쓴다. M4 의 센서 모델이 여기서 쓰인다.
3. **재샘플링:** 가중치에 비례해 파티클을 다시 뽑는다. 그럴듯한 가설은 복제되고, 틀린 가설은
   사라진다. 베이즈 필터의 보정 단계를 샘플로 구현한 것이다.

### 재샘플링의 함정

매 스텝 재샘플링하면 다양성이 빨리 줄어든다(**샘플 고갈**). 그래서 가중치가 한쪽에 쏠렸을 때만
재샘플링하고, 쏠림 정도를 유효 파티클 수 $N_\text{eff}$ 로 잰다. 계통 재샘플링은 균일 난수 하나로
등간격 포인터를 만들어 분산이 작고 $O(N)$ 이다.

### MCL 과 AMCL

- **전역 위치 추정:** 처음에 지도 전체에 파티클을 뿌리면 위치를 몰라도 수렴한다. 칼만 필터로는
  어렵다.
- **납치 로봇 문제:** 누가 로봇을 들어서 옮기면 모든 파티클이 틀린다. 일부 파티클을 무작위로
  다시 뿌려 회복한다.
- **AMCL:** 불확실할 때 파티클을 늘리고 수렴하면 줄이는(KLD 샘플링) 적응형 MCL. Nav2 에서
  `map → odom` 변환을 발행한다(M8 tf2 레슨의 프레임 트리 참조).

비용은 계산량이다. 상태 차원이 커지면 필요한 파티클 수가 지수적으로 늘기 때문에, 파티클 필터는
로봇 자세(3차원) 같은 저차원 문제에서 주로 쓴다.

## 핵심 수식

가중치와 정규화:

$$w^{[i]} \propto p(z_t \mid x_t^{[i]}),\qquad \sum_i w^{[i]} = 1$$

독립 거리 측정 여러 개면 우도는 곱이다: $p(z \mid x) = \prod_j \mathcal{N}(z_j;\ \lVert x - m_j \rVert,\ \sigma^2)$.

유효 파티클 수:

$$N_\text{eff} = \frac{1}{\sum_i \left(w^{[i]}\right)^2}$$

$N_\text{eff} < N/2$ 일 때 재샘플링하는 것이 흔한 규칙이다. 추정값은 가중 평균 $\hat x = \sum_i w^{[i]} x^{[i]}$.

## 예제

10 m × 10 m 공간에 랜드마크 4 개가 있고, 로봇은 매 스텝 (0.3, 0.2) m 씩 움직이며 각 랜드마크까지
거리를 잰다($\sigma = 0.3$ m). 파티클 500 개를 공간 전체에 균일하게 뿌려 시작한다(전역 위치 추정).

```python
import numpy as np

rng = np.random.default_rng(3)
landmarks = np.array([[1.0, 1.0], [9.0, 1.0], [1.0, 9.0], [9.0, 9.0]])
N, sigma_move, sigma_range = 500, 0.1, 0.3

x_true = np.array([2.0, 3.0])
particles = rng.uniform(0, 10, size=(N, 2))  # 처음엔 위치를 모른다
weights = np.full(N, 1 / N)


def systematic_resample(weights):
    positions = (rng.random() + np.arange(N)) / N
    return np.searchsorted(np.cumsum(weights), positions).clip(max=N - 1)


for t in range(15):
    u = np.array([0.3, 0.2])
    x_true = x_true + u + rng.normal(0, sigma_move, 2)
    z = np.linalg.norm(landmarks - x_true, axis=1) + rng.normal(0, sigma_range, 4)

    particles += u + rng.normal(0, sigma_move, particles.shape)  # 1) 예측
    pred = np.linalg.norm(particles[:, None, :] - landmarks[None], axis=2)
    weights *= np.exp(-0.5 * np.sum((pred - z) ** 2, axis=1) / sigma_range**2)  # 2) 가중치
    weights += 1e-300
    weights /= weights.sum()

    n_eff = 1 / np.sum(weights**2)
    if n_eff < N / 2:  # 3) 필요할 때만 재샘플링
        particles = particles[systematic_resample(weights)]
        weights = np.full(N, 1 / N)

    est = weights @ particles
    if t in (0, 1, 4, 14):
        err = np.linalg.norm(est - x_true)
        print(f"t={t:2d} 오차 {err:.2f} m, 퍼짐 {particles.std(axis=0).mean():.2f} m")
```

시작할 때 파티클은 방 전체(표준편차 약 2.9 m)에 퍼져 있지만, 랜드마크 4 개의 거리가 위치를
강하게 제약하므로 **첫 관측과 재샘플링 한 번**만에 구름이 0.2 m 정도로 모이고 오차도 측정 잡음
수준(약 0.1–0.2 m)이 된다. 랜드마크가 적거나 대칭이면 이 수렴이 훨씬 느려진다(연습 과제 2).

**연습 과제(exercise):** (1) `N` 을 50, 500, 5000 으로 바꿔 수렴 속도와 실행 시간을 비교하라.
(2) 랜드마크를 하나만 남기면 파티클 구름이 어떤 모양(원호)이 되는지 그려라. (3) 10 번째 스텝에서
`x_true` 를 멀리 옮기는 "납치"를 넣고, 매 스텝 파티클 5% 를 무작위로 다시 뿌리는 방법으로 회복시켜라.

## 자가 점검 질문

1. 재샘플링을 매 스텝 무조건 하면 어떤 문제가 생기며, $N_\text{eff}$ 는 이를 어떻게 완화하는가?
2. 똑같은 복도 두 개가 있는 지도에서 EKF 와 MCL 의 전역 위치 추정 결과가 어떻게 다를지 설명하라.
3. 예제 코드에서 `weights += 1e-300` 이 없을 때 생길 수 있는 수치 문제는 무엇인가?

## 이 단계 공부법

1. **영상(먼저):** Stachniss "Particle Filter & MCL" 로 세 단계와 재샘플링 그림을 익힌다.
2. **교재 + 노트북:** Labbe 의 Particle Filters 장을 실행한다. 재샘플링 방식 비교 부분을 특히 본다.
3. **본문 + 예제:** 예제를 돌린 뒤 연습 과제 (1)–(3)을 한다. 파티클을 산점도로 매 스텝 그려 보면
   직관이 크게 는다.
4. **심화(선택):** *Probabilistic Robotics* Ch. 8 에서 MCL·KLD 샘플링을 읽고, Nav2 의 AMCL
   파라미터(`min_particles`, `max_particles`)가 무엇에 대응하는지 연결한다.

## 참고 자료

- Cyrill Stachniss, "Particle Filter & MCL" — <https://www.youtube.com/watch?v=MsYlueVDLI0>
- Roger Labbe, *Kalman and Bayesian Filters in Python*, Particle Filters 장 —
  <https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python>
- Sebastian Thrun, Wolfram Burgard, Dieter Fox, *Probabilistic Robotics*, MIT Press —
  <https://robots.stanford.edu/probabilistic-robotics/>
- University of Michigan, ROB 530 Mobile Robotics — <https://github.com/UMich-CURLY-teaching/UMich-ROB-530-public>
