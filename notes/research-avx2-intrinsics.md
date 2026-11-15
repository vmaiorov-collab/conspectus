# AVX2-интринсики в C++: заметки по первоисточникам

Материал для лекции «Testing, C++, AVX». Дата сбора: 2026-11-15.

## Как читать заметки

Каждое утверждение снабжено URL владельца. Метки в тексте:

- **[источник]** — прочитано в первоисточнике (цитата или близкий пересказ).
- **[проверено]** — проверено компиляцией и запуском здесь (g++ 13.3.0, clang++ 18.1.3, Linux x86-64, CPU с AVX2).
- **[не проверено]** — не удалось подтвердить первоисточником. Подробности в разделе «Что не проверено».

Источники:

| Сокращение | Что это | URL |
|---|---|---|
| Intel Guide | Intel Intrinsics Guide v3.6.9 (07/12/2024). Сама страница грузит данные JS-ом, поэтому текст взят из XML-данных, на которых она построена | https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html, данные: https://www.intel.com/content/dam/develop/public/us/en/include/intrinsics-guide/data-latest.xml |
| SDM | Intel 64 and IA-32 Architectures SDM, Combined Volumes, Order Number 325462-093US (в файле стоит дата «September 2026») | https://cdrdv2.intel.com/v1/dl/getContent/671200 |
| GCC manual | Документация GCC | https://gcc.gnu.org/onlinedocs/gcc/ |
| Clang docs | Документация Clang | https://clang.llvm.org/docs/ |
| C++ draft | Черновик стандарта C++ (используется вместо cppreference, см. ниже) | https://eel.is/c++draft/ |

---

## 1. Заголовок и типы

- Все интринсики, которые мы разбираем, в Intel Guide имеют заголовок `immintrin.h` **[источник]** (поле `header` в XML-данных, https://www.intel.com/content/dam/develop/public/us/en/include/intrinsics-guide/data-latest.xml). Исключение: 128-битные вроде `_mm_cvtsi128_si32` лежат в `emmintrin.h`, но `immintrin.h` их подтягивает.
- Типы `__m256` (8 float), `__m256i` (целые, 256 бит), `__m256d` (4 double) в GCC — это обычные векторные типы с `__vector_size__ (32)` и `__may_alias__`. Базовый тип `__m256i` — `long long` (4 элемента), то есть тип не несёт информации о ширине элемента **[проверено]**: файл `avxintrin.h` из GCC 13.3 (`/usr/lib/gcc/x86_64-linux-gnu/13/include/avxintrin.h`, строки 55–69). Там же есть `__m256i_u` (невыровненный вариант).
- Механизм векторных типов GCC (`vector_size`) описан здесь: https://gcc.gnu.org/onlinedocs/gcc/Vector-Extensions.html. Там же сказано, что обычные операторы работают поэлементно и что такой код можно смешивать с интринсиками **[источник]**.
- Clang: векторные типы GCC создаются атрибутом `vector_size(N)`, где N — число байт **[источник]** https://clang.llvm.org/docs/LanguageExtensions.html.
- Важно для лекции: заголовок `immintrin.h` можно включать и без `-mavx2`. Но вызов `_mm256_add_epi32` из функции без включённого AVX2 даст ошибку компиляции. GCC: `inlining failed in call to 'always_inline' ... target specific option mismatch` **[проверено]**. Clang: `always_inline function ... requires target feature 'avx2'` **[проверено]**.

## 2. Схема имён

В первоисточниках (Intel Guide) нет отдельной страницы с формальной грамматикой имён, поэтому ниже **наблюдение по данным Intel Guide**, а не цитата правила. Форма: `_mm256_<операция>_<суффикс типа>`.

Суффиксы в наблюдаемых именах (https://www.intel.com/content/dam/develop/public/us/en/include/intrinsics-guide/data-latest.xml):

| Суффикс | Смысл (по описаниям в Intel Guide) | Пример |
|---|---|---|
| `epi32` | упакованные знаковые 32-битные целые | `_mm256_add_epi32` |
| `epi64` | упакованные 64-битные целые | `_mm256_add_epi64` |
| `epi16`, `epi8` | 16- и 8-битные целые | `_mm256_madd_epi16`, `_mm256_movemask_epi8` |
| `si256` | весь регистр как «просто биты» | `_mm256_loadu_si256` |
| `ps`, `pd` | упакованные float и double | `_mm256_movemask_ps`, `_mm256_fmadd_ps` |

- Префикс `_mm_` — 128 бит (XMM), `_mm256_` — 256 бит (YMM). Пример 128-битной формы: `_mm_cvtsi128_si32` (Intel Guide, тот же XML).
- Каждая запись в Intel Guide содержит поле `CPUID` — какой набор инструкций нужен. Для `_mm256_add_epi32`, `_mm256_mullo_epi32`, `_mm256_madd_epi16`, `_mm256_cmpgt_epi32`, `_mm256_blendv_epi8`, `_mm256_permutevar8x32_epi32` и других целочисленных 256-битных операций это `AVX2`. А `_mm256_loadu_si256`, `_mm256_setzero_si256`, `_mm256_movemask_ps` требуют только `AVX`. `_mm256_fmadd_ps` требует отдельный флаг `FMA` **[источник]** (тот же XML). Вывод для лекции: «целочисленный 256-битный код = AVX2», FMA нужно включать отдельно (`-mfma` или `target("avx2,fma")`).

## 3. Загрузка и сохранение, выравнивание

Данные из Intel Guide (https://www.intel.com/content/dam/develop/public/us/en/include/intrinsics-guide/data-latest.xml):

| Интринсик | Что сказано |
|---|---|
| `_mm256_load_si256(__m256i const*)` | «mem_addr must be aligned on a 32-byte boundary or a general-protection exception may be generated» |
| `_mm256_loadu_si256(__m256i const*)` | «does not need to be aligned on any particular boundary» |
| `_mm256_store_si256` / `_mm256_storeu_si256` | то же самое для записи |
| `_mm256_lddqu_si256` | «may perform better than _mm256_loadu_si256 when the data crosses a cache line boundary» |

- **[проверено]** `_mm256_load_si256` по адресу `buf+1` (смещение 4 байта) на Linux с g++ 13 -O2 приводит к `Segmentation fault` (#GP превращается в SIGSEGV). Выровненный адрес работает.
- SDM, Vol. 1, §14.9 «Memory alignment» (https://cdrdv2.intel.com/v1/dl/getContent/671200): у инструкций с VEX-кодировкой требования к выравниванию мягче, чем у SSE. Исключение составляют явно выровненные 16- и 32-байтные load/store (`VMOVDQA` и подобные), они требуют выравнивания. Там же: «Software may see performance penalties when unaligned accesses cross cacheline boundaries, so reasonable attempts to align commonly used data sets should continue to be pursued.» **[источник]**
- Практический вывод для соревновательного кода: по умолчанию использовать `loadu`/`storeu`. Выровненные версии нужны, только если вы сами гарантируете выравнивание.
- Выравнивание в C++: `alignas(32)` — стандартный спецификатор. Если реализация не поддерживает запрошенное расширенное выравнивание, программа некорректна (ill-formed) **[источник]** https://eel.is/c++draft/dcl.align. На cppreference получить страницы не удалось (см. «Что не проверено»).
- Приведение `reinterpret_cast<const __m256i*>(int*)`: общая формулировка правил доступа в стандарте — https://eel.is/c++draft/basic.lval (допустимые типы доступа: тот же тип, соответствующий знаковый/беззнаковый, `char`, `unsigned char`, `std::byte`). В GCC типы `__m256i` объявлены с `__may_alias__` **[проверено]** (`avxintrin.h`, см. выше), поэтому на практике это приведение работает в GCC; но это свойство реализации, а не стандарта C++.

## 4. Целочисленная арифметика

Описания из Intel Guide (https://www.intel.com/content/dam/develop/public/us/en/include/intrinsics-guide/data-latest.xml):

- `_mm256_add_epi32(a, b)`, `_mm256_sub_epi32(a, b)` — поэлементные сложение и вычитание 32-битных (в `sub` результат: `a - b`). Переполнение: в псевдокоде Intel Guide — просто `a + b` над 32 битами, то есть по модулю 2^32.
- `_mm256_mullo_epi32(a, b)` — умножение 32×32 с сохранением **младших 32 бит** произведения (intermediate 64-bit, в `dst` пишутся `tmp[31:0]`).
- `_mm256_mul_epi32(a, b)` — умножает только **младшие** 32 бита каждого 64-битного элемента, результат 64 бита (4 произведения).
- `_mm256_madd_epi16(a, b)` — умножает знаковые 16-битные пары и складывает **соседние** пары, получая 8 значений int32: `a[2k]*b[2k] + a[2k+1]*b[2k+1]`. Это основной строительный блок скалярного произведения для int16.
- `_mm256_cvtepi32_epi64(__m128i)` — расширение знаковых 32-битных до 64-битных (4 элемента), удобно для суммы без переполнения.
- Сдвиги: `_mm256_slli_epi32(a, imm8)` — при счётчике больше 31 даёт 0.

## 5. Сравнение, blend, movemask

Из Intel Guide (тот же XML):

- `_mm256_cmpeq_epi32`, `_mm256_cmpgt_epi32` дают маску поэлементно: `0xFFFFFFFF` если условие истинно, иначе 0. Сравнение `cmpgt` — **знаковое**. Беззнакового `cmpgt` в AVX2 нет (эту фразу как «в AVX2 нет» я проверил только по отсутствию такой записи в данном XML, отдельного заявления в SDM не искал).
- `_mm256_blendv_epi8(a, b, mask)` — для каждого байта берёт `b`, если старший бит байта маски равен 1, иначе `a`. Поэтому маску из `cmpgt` можно подавать напрямую (все байты элемента одинаковы).
- `_mm256_blend_epi32(a, b, imm8)` — выбор по биту константы `imm8` (константа времени компиляции).
- `_mm256_movemask_epi8(a)` — 32-битная маска из старших бит байтов; `_mm256_movemask_ps(__m256)` — 8-битная маска из знаковых бит 8 float. Типичный приём: `cmpgt` → `castsi256_ps` → `movemask_ps` → `popcount` (счёт элементов) или `ctz` (индекс первого). `_mm256_castsi256_ps` в тексте Intel Guide для `_mm256_castsi256_si128` описан как не генерирующий инструкций, аналогично для остальных cast — **[источник]** только для `castsi256_si128`.

## 6. Перестановки и ограничение «128-битных полос»

- SDM, Vol. 1, §14.6.1 (https://cdrdv2.intel.com/v1/dl/getContent/671200): «Generally, most of the promoted 256-bit vector integer instructions follow the 128-bit lane operation». Новые межполосные возможности в AVX2 дают отдельные инструкции broadcast и permute, а из старых «cross-lane» ведут себя, например, семейства `VPMOVZ/VPMOVS` **[источник]**.
- В таблице SDM (Vol. 1, гл. 14) `VPERMILPS/VPERMILPD` помечены `in-lane`, а `VPERMD`, `VPERMPS`, `VPERMQ`, `VPERMPD` — `cross-lane` **[источник]**.
- Intel Guide (тот же XML):
  - `_mm256_shuffle_epi32(a, imm8)` — «within 128-bit lanes»: одна и та же перестановка применяется независимо к нижней и верхней половинам.
  - `_mm256_shuffle_epi8(a, b)` — тоже внутри 128-битных полос; индекс берётся из младших 4 бит байта `b`, а установленный старший бит даёт ноль.
  - `_mm256_permutevar8x32_epi32(a, idx)` — «across lanes»: произвольная перестановка 8 элементов int32 по индексам `idx[2:0]`.
  - `_mm256_permute2x128_si256(a, b, imm8)` — выбор двух 128-битных половин из `a` и `b` (с возможностью обнулить).
  - `_mm256_extracti128_si256(a, imm8)` — достать нижнюю (0) или верхнюю (1) половину; `_mm256_castsi256_si128(a)` — нижняя половина без инструкции.
- Следствие для лекции: «сложить два соседних элемента через границу полос» напрямую нельзя, нужно `permutevar8x32`, `permute2x128` или `extracti128`.

## 7. Горизонтальные суммы

- `_mm256_hadd_epi32(a, b)` складывает соседние пары **внутри каждой полосы**; результат: `a01, a23, b01, b23 | a45, a67, b45, b67` (псевдокод в Intel Guide, https://www.intel.com/content/dam/develop/public/us/en/include/intrinsics-guide/data-latest.xml). Из-за полос одного `hadd` для суммы всех 8 элементов недостаточно.
- Типичная схема суммы 8 элементов int32 (рабочий код в разделе 12, пример 2): сложить две половины (`extracti128` + `castsi256_si128` + `_mm_add_epi32`), затем два раза сложить с `_mm_shuffle_epi32`, в конце `_mm_cvtsi128_si32`. **[проверено]**
- Главное правило оптимизации: накапливать сумму в векторе внутри цикла, а горизонтальную сумму брать **один раз после цикла**.
- Утверждение «`hadd` медленный» **[не проверено]**: в первоисточниках, которые я успел прочитать, цифр задержек не читал (Intel Guide хранит их по микроархитектурам, но я их не извлекал).

## 8. Как включить AVX2

### 8.1. Флаг компилятора

- GCC: `-mavx2` — «Support MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, AVX and AVX2 built-in functions and code generation» **[источник]** https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html. Там же: `-march=native` выбирает процессор по машине, на которой идёт компиляция, и включает все поддерживаемые ею наборы инструкций **[источник]**. Опасность для судей: бинарник, собранный с `-march=native` или `-mavx2`, может упасть с `SIGILL` на машине без AVX2.

### 8.2. `#pragma GCC target`

- «This pragma allows you to set target-specific options for functions defined later in the source file»; реализован для x86 и ряда других архитектур **[источник]** https://gcc.gnu.org/onlinedocs/gcc/Function-Specific-Option-Pragmas.html. Там же `#pragma GCC push_options` / `pop_options` хранят стек текущих опций target и optimize.
- **[проверено]** `#pragma GCC target("avx2")` перед `#include <bits/stdc++.h>` и `<immintrin.h>` работает в g++ 13.3 (программа печатает 16).
- **[проверено]** Clang 18.1.3 эту прагму **не** учитывает: компиляция того же файла падает с `always_inline function '_mm256_loadu_si256' requires target feature 'avx'...`. Для Clang нужен атрибут или флаг. В документации Clang об этом я отдельного явного утверждения не читал, только проверил поведение.

### 8.3. Атрибут `target`

- GCC: `__attribute__((target("avx2")))` — в списке опций x86 есть `avx2`: «Enable/disable the generation of the AVX2 instructions» **[источник]** https://gcc.gnu.org/onlinedocs/gcc/x86-Attributes.html.
- Там же про инлайнинг: «On the x86, the inliner does not inline a function that has different target options than the caller, unless the callee has a subset of the target options of the caller» **[источник]**. Практически: обычная функция без `avx2` не может инлайнить функцию с `target("avx2")`; вызов превращается в обычный call.
- Clang: атрибут `target` поддерживается, для x86 допускает ещё `tune="CPU"`, а у мультиверсионных функций должна быть реализация `default` **[источник, частично]** https://clang.llvm.org/docs/AttributeReference.html. Раздел читал не целиком (длинная страница, часть ответа получена фрагментом).
- **[проверено]** Все три примера из раздела 12 с `__attribute__((target("avx2")))` собираются без `-mavx2` и верно работают в g++ 13.3 и clang++ 18.1.3.

### 8.4. `target_clones` (авто-диспетчеризация)

- GCC: «The `target_clones` attribute is used to specify that a function be cloned into multiple versions compiled with different target options than specified on the command line». Пример из документации: `target_clones("sse4.1,avx")` порождает два клона **[источник]** https://gcc.gnu.org/onlinedocs/gcc/Common-Attributes.html.
- Я не собирал пример с `target_clones("avx2,default")` — **[не проверено]** компиляцией.

## 9. Определение процессора во время выполнения

### 9.1. `__builtin_cpu_supports`

- GCC: «returns a positive integer if the run-time CPU supports feature and returns 0 otherwise»; имя признака — `"avx2"` («AVX2 instructions»). `__builtin_cpu_init` нужно вызывать явно только в функциях, выполняемых до конструкторов (например, ifunc-резолверы); в обычном `main` определение CPU уже выполнено высокоприоритетным конструктором **[источник]** https://gcc.gnu.org/onlinedocs/gcc/x86-Built-in-Functions.html.
- Clang: «detects if the run-time CPU supports features specified in string argument», возвращает положительное число, если поддержаны все признаки **[источник]** https://clang.llvm.org/docs/LanguageExtensions.html. Про `__builtin_cpu_init`/`__builtin_cpu_is` в прочитанном фрагменте Clang данных нет.
- **[проверено]** Использование: `if (__builtin_cpu_supports("avx2")) sum_avx2(...); else sum_scalar(...);` — работает в g++ и clang++ (раздел 12).

### 9.2. CPUID (на что опирается проверка)

SDM, Vol. 1, §14.7.1 «Detection of Intel AVX2» (https://cdrdv2.intel.com/v1/dl/getContent/671200) **[источник]**:

1. `CPUID.01H:ECX` — должны быть установлены оба бита: OSXSAVE (бит 27) и AVX (бит 28) (маска `018000000H`).
2. `CPUID.07H.00H:EBX.AVX2[5] = 1` (маска `20H`).
3. `XGETBV` с ECX=0: `XCR0 & 06H == 06H` — ОС включила сохранение состояния XMM и YMM.

Все три шага нужны. Одного бита AVX2 в CPUID недостаточно, если ОС не включила YMM-состояние. `__builtin_cpu_supports("avx2")` скрывает эти проверки (что именно проверяет реализация GCC, в документации GCC не расписано — **[не проверено]**, что она проверяет XCR0).

## 10. Автовекторизация против интринсиков

- GCC: `-O2` включает `-ftree-loop-vectorize`, `-ftree-slp-vectorize` и `-fvect-cost-model=very-cheap`; `-O3` ставит `-fvect-cost-model=dynamic`. `-ftree-vectorize` включает оба вида векторизации **[источник]** https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html.
- Диагностика: `-fopt-info` управляет дампами оптимизаций, ключевое слово `vec` включает «dumps from all vectorization optimizations» **[источник]** https://gcc.gnu.org/onlinedocs/gcc/Developer-Options.html.
- `-fassociative-math`: «Allow re-association of operands in series of floating-point operations», требует `-fno-signed-zeros` и `-fno-trapping-math`; `-ffast-math` включает группу небезопасных оптимизаций **[источник]** https://gcc.gnu.org/onlinedocs/gcc/Optimize-Options.html. Отсюда (вывод, не цитата): сумму float компилятор без этих флагов не векторизует, потому что смена порядка сложения меняет результат; сумму целых векторизует.
- **[проверено]** g++ 13.3, два цикла суммы (`int -> long long` и `float`), флаги `-fopt-info-vec-optimized`:
  - `-O2` (без `-mavx2`): ни одного сообщения о векторизации;
  - `-O2 -mavx2`: тоже ни одного сообщения (причины не исследовал; возможно, дело в `very-cheap` cost model, это гипотеза);
  - `-O3 -mavx2 -ffast-math`: векторизованы оба цикла («loop vectorized using 32 byte vectors» и 16 byte).
  - Отдельно `-O3 -mavx2` без `-ffast-math` я не запускал, поэтому вывод «float без fast-math не векторизуется» подтверждён только логикой документации (`-fassociative-math`), не запуском.
- Альтернатива интринсикам — расширение `vector_size` GCC/Clang (https://gcc.gnu.org/onlinedocs/gcc/Vector-Extensions.html).

## 11. Подводные камни

1. **Переход AVX↔SSE и `vzeroupper`.** SDM Vol. 1 §14.8: старые SSE-инструкции (без VEX-префикса) не трогают биты 255:128 регистров YMM, а VEX.128-инструкции обнуляют верхние 128 бит **[источник]**. SDM Vol. 2C, описание `VZEROUPPER`: «This instruction is recommended when transitioning between AVX and legacy SSE code; it will eliminate performance penalties caused by false dependencies» **[источник]**. Интринсики: `_mm256_zeroupper()` (обнуляет верхние 128 бит всех YMM; `_mm256_zeroall()` обнуляет все регистры целиком) **[источник]** Intel Guide. GCC: `-mvzeroupper` заставляет компилятор вставлять `vzeroupper` перед выходом из функции «to minimize the AVX to SSE transition penalty» **[источник]** https://gcc.gnu.org/onlinedocs/gcc/x86-Options.html. **[проверено]** В ассемблере моего теста GCC 13 сам вставил `vzeroupper` (3 вхождения). Размер штрафа (разные микроархитектуры) я из первоисточников не извлекал — **[не проверено]**. В SDM добавлено: смешивание SSE и AVX внутри транзакционной области (RTM) может привести к её откату **[источник]** (Vol. 1, раздел о TSX).
2. **Невыровненный доступ.** `load`/`store` вместо `loadu`/`storeu` — #GP и SIGSEGV (разд. 3, **[проверено]**). Пересечение границы кэш-линии замедляет (SDM §14.9).
3. **Хвост массива.** Длина n не кратна 8: нужно обработать остаток отдельным скалярным циклом (разд. 12) либо `_mm256_maskload_epi32`/`maskstore` (в Intel Guide: элементы с невыставленным старшим битом маски обнуляются) **[источник]**. Не читайте за концом массива без масок: безопасность `maskload` на границе страницы (подавляются ли ошибки для замаскированных элементов) я по первоисточникам не проверял — **[не проверено]**.
4. **Переполнение.** `add_epi32`/`mullo_epi32` дают результат по модулю 2^32 (разд. 4); `madd_epi16` складывает пару произведений в int32 и может переполниться на крайних значениях (в псевдокоде Intel Guide нет насыщения).
5. **Сервера проверки (судьи) могут не иметь AVX2.** Первоисточника с утверждением про конкретные судьи нет, это общий вывод из того, что инструкция AVX2 требует CPUID-флага (SDM §14.7.1). Защита: `__builtin_cpu_supports("avx2")` с запасной скалярной веткой, `target`-атрибут вместо глобального `-mavx2`/`-march=native`. **[не проверено]** на реальных судьях.
6. **Передача `__m256i` по значению.** GCC при компиляции без AVX предупреждает: `the ABI for passing parameters with 32-byte alignment has changed in GCC 4.6` (замечено в моём тесте на функции с параметром `__m256i` без включённого AVX; Clang в такой ситуации выдал ошибку `AVX vector return of type '__m256i' ... without 'avx' enabled changes the ABI`) **[проверено]**.
7. **`#pragma GCC target` и `bits/stdc++.h`.** В моём тесте g++ 13.3 работает; общих гарантий для разных версий не искал — **[не проверено]**.

## 12. Примеры C++17 (скомпилированы и запущены)

Статус: **[проверено]**. Компиляция: `g++ -std=c++17 -O2 -Wall -Wextra ex.cpp` и `clang++ -std=c++17 -O2 -Wall -Wextra ex.cpp`; также `g++ -O1 -g -fsanitize=address,undefined`. Все три сборки напечатали `OK` для n ∈ {0, 1, 7, 8, 9, 15, 16, 17, 1000, 100003}; сверка идёт со скалярной версией. Флаг `-mavx2` не использовался: AVX2 включается атрибутом `target`. Машина, где запускалось: x86-64 с AVX2 (флаг `avx2` виден в `/proc/cpuinfo`).

```cpp
#include <immintrin.h>
#include <cstdint>
#include <cstddef>

// Пример 1. Сумма int32 -> int64 (без переполнения).
__attribute__((target("avx2")))
long long sum_avx2(const int* a, size_t n) {
    __m256i acc = _mm256_setzero_si256();            // 4 x int64
    size_t i = 0;
    for (; i + 8 <= n; i += 8) {
        __m256i v  = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(a + i));
        __m256i lo = _mm256_cvtepi32_epi64(_mm256_castsi256_si128(v));
        __m256i hi = _mm256_cvtepi32_epi64(_mm256_extracti128_si256(v, 1));
        acc = _mm256_add_epi64(acc, _mm256_add_epi64(lo, hi));
    }
    alignas(32) long long t[4];
    _mm256_store_si256(reinterpret_cast<__m256i*>(t), acc);
    long long s = t[0] + t[1] + t[2] + t[3];
    for (; i < n; ++i) s += a[i];                    // хвост
    return s;
}

// Пример 2. Скалярное произведение int16 -> int32 через madd.
// Внимание: сумма должна помещаться в int32 (в тесте значения в [-100, 100]).
__attribute__((target("avx2")))
int dot_avx2(const int16_t* a, const int16_t* b, size_t n) {
    __m256i acc = _mm256_setzero_si256();            // 8 x int32
    size_t i = 0;
    for (; i + 16 <= n; i += 16) {
        __m256i x = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(a + i));
        __m256i y = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(b + i));
        acc = _mm256_add_epi32(acc, _mm256_madd_epi16(x, y));
    }
    // горизонтальная сумма один раз после цикла
    __m128i s = _mm_add_epi32(_mm256_castsi256_si128(acc),
                              _mm256_extracti128_si256(acc, 1));
    s = _mm_add_epi32(s, _mm_shuffle_epi32(s, 0x4E));
    s = _mm_add_epi32(s, _mm_shuffle_epi32(s, 0xB1));
    int r = _mm_cvtsi128_si32(s);
    for (; i < n; ++i) r += a[i] * b[i];             // хвост
    return r;
}

// Пример 3. Число элементов > x: cmpgt + movemask_ps + popcount.
__attribute__((target("avx2,popcnt")))
size_t count_gt_avx2(const int* a, size_t n, int x) {
    const __m256i vx = _mm256_set1_epi32(x);
    size_t i = 0, c = 0;
    for (; i + 8 <= n; i += 8) {
        __m256i v = _mm256_loadu_si256(reinterpret_cast<const __m256i*>(a + i));
        __m256i m = _mm256_cmpgt_epi32(v, vx);
        c += __builtin_popcount(_mm256_movemask_ps(_mm256_castsi256_ps(m)));
    }
    for (; i < n; ++i) c += a[i] > x;
    return c;
}

// Диспетчеризация во время выполнения:
//   __builtin_cpu_init();
//   if (__builtin_cpu_supports("avx2")) s = sum_avx2(a, n); else s = sum_scalar(a, n);
```

Примечание: в тестовом файле были ещё скалярные эталоны и `main` с проверкой `__builtin_cpu_init(); __builtin_cpu_supports("avx2")`; здесь они опущены. Блок «Диспетчеризация» в конце листинга — схема; `sum_scalar` в ней условное имя, как отдельный код он не собирался.

## 13. Что не проверено

- **cppreference**: страницы `alignas`, `aligned_alloc`, `reinterpret_cast` вернули HTTP 403; повторять запрос с изменёнными заголовками я не стал. Вместо них использован черновик стандарта (https://eel.is/c++draft/). Утверждения про `std::aligned_alloc` (требование «размер кратен выравниванию») и про `operator new` с выравниванием в C++17 здесь **не подтверждены** и в конспект не вынесены.
- **Intel Intrinsics Guide** как веб-страница читается только JS-ом. Использованы XML-данные с того же сайта (версия 3.6.9, 07/12/2024), не отрисованный интерфейс. Таблицы задержек/пропускной способности не извлекались.
- **Размер штрафа** AVX↔SSE и цифры производительности `hadd`, `gather`: не извлекались из первоисточников. Нужен Intel Optimization Reference Manual (его я не открывал).
- **Clang**: страницы `AttributeReference` и `LanguageExtensions` длинные и читались фрагментами; `target_clones`, `cpu_dispatch`/`cpu_specific` и `__builtin_cpu_init` в Clang не подтверждены.
- **Реализация `__builtin_cpu_supports`**: учитывает ли она XCR0 (поддержку ОС) — документация GCC этого не говорит.
- **`target_clones("avx2,default")`**: пример из документации прочитан, но сам я его не собирал.
- **Судьи без AVX2**: первоисточника нет; это инженерный вывод.
- Дата SDM в самом файле — «September 2026», нумерация 325462-093US; других версий для сверки я не брал.
- Тесты проводились на одной машине (g++ 13.3.0, clang++ 18.1.3): другие версии компиляторов могут вести себя иначе (особенно `#pragma GCC target`, сообщения диагностики и автовекторизация на `-O2`).
