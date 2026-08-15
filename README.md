# WG-PROTON-CFG-TO-V2RAYN-CFG

1. What it is for?

For quickly and effortlessly importing WireGuard configurations (including
ProtonVPN) into v2rayN (as well as Sing-box, Xray, Nekoray) without the hassle
of manually copying and typing keys, IP addresses, and ports.

2. What it does

  - Scans the local folder to automatically find all configuration files (.conf
    and .txt).
  - Extracts key parameters: private/public keys, endpoints, IP addresses,
    ports, MTU, Keepalive, and server names.
  - Generates standard URI links in the wireguard://... format supported by
    v2rayN.
  - Saves all links to a file (generated_links.txt) and displays an interactive
    console menu that allows you to copy any link directly to your clipboard
    with a single keystroke.

3. Step-by-step instructions

1.  Place the files: Put your .conf or .txt files into the same folder as the
    program.
2.  Run the program: Press Enter in the terminal to process the files.
3.  Select a server: Type the number of the desired server from the list — its
    link will be copied directly to your clipboard.
4.  Paste into v2rayN: Open the v2rayN app and press Ctrl + V. The server is now
    added and ready to connect.

===============================================

1. Для чего?

Для быстрого и удобного переноса настроек WireGuard (включая ProtonVPN) в клиент
v2rayN (а также Sing-box, Xray, Nekoray) без необходимости вручную
перепечатывать ключи, IP-адреса и порты.

2. Что она делает

  - Сканирует папку рядом с собой и находит все файлы конфигураций (.conf и
    .txt).
  - Извлекает параметры: приватные/публичные ключи, адреса, порты, MTU,
    Keepalive и названия серверов.
  - Генерирует ссылки единого формата wireguard://..., которые понимает v2rayN.
  - Сохраняет всё в файл generated_links.txt и выводит меню в консоли, где по
    нажатию цифры копирует выбранную ссылку прямо в буфер обмена.

3. Последовательность действий

1.  Положить файлы: закинуть ваши .conf или .txt файлы в папку с программой.
2.  Запустить программу: нажать Enter в консоли для старта обработки.
3.  Выбрать сервер: ввести номер нужной конфигурации из списка — ссылка сразу
    скопируется в буфер обмена.
4.  Вставить в v2rayN: открыть приложение v2rayN и нажать Ctrl + V. Сервер готов
    к работе.
