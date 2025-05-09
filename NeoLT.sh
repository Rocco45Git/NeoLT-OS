#!/bin/bash

NEOLT_DIR="$HOME/.neolt"
USERS_FILE="$NEOLT_DIR/users"
SETTINGS_FILE="$NEOLT_DIR/settings"
DARK_MODE=false
CURRENT_USER=""
ROWS=$(tput lines)

function set_theme() {
  if $DARK_MODE; then
    FG="\e[97m"
    BG="\e[40m" # Black
  else
    FG="\e[30m"
    BG="\e[107m" # White
  fi
}

function draw_bg() {
  set_theme
  clear
  for ((i=0; i<ROWS; i++)); do
    echo -ne "${BG}                                                                                \e[0m\n"
  done
}

function color_echo() {
  set_theme
  echo -e "${BG}${FG}$1\e[0m"
}

function setup_neolt() {
  clear
  echo -e "\e[96m===============================\e[0m"
  echo -e "\e[93m      Welcome to NeoLT OS      \e[0m"
  echo -e "\e[96m===============================\e[0m"
  echo ""
  echo "First-time setup..."

  mkdir -p "$NEOLT_DIR"
  echo "dark=false" > "$SETTINGS_FILE"
  touch "$USERS_FILE"

  create_user
  echo "Setup complete! Re-run ./neoLT.sh to start NeoLT."
  exit 0
}

function load_settings() {
  if grep -q "dark=true" "$SETTINGS_FILE"; then
    DARK_MODE=true
  else
    DARK_MODE=false
  fi
}

function create_user() {
  read -p "Choose a username: " new_user
  read -s -p "Choose a password: " new_pass
  echo ""
  echo "$new_user:$new_pass" >> "$USERS_FILE"
  echo "User '$new_user' created!"
}

function powerwash() {
  read -p "Are you sure you want to erase NeoLT? (yes to confirm): " confirm
  if [[ "$confirm" == "yes" ]]; then
    rm -rf "$NEOLT_DIR"
    echo "System reset complete. Re-run ./neoLT.sh to set up again."
    exit 0
  else
    echo "Powerwash cancelled."
    sleep 1
  fi
}

function boot_screen() {
  draw_bg
  tput cup 2 0
  color_echo "============== N E O L T   O S =============="
  color_echo "       A Terminal-Based OS Experience        "
  color_echo "============================================"
  sleep 1
}

function login_screen() {
  boot_screen
  color_echo "Login or type 'powerwash' to reset system."
  echo -n "Username: "
  read input_user
  if [[ "$input_user" == "powerwash" ]]; then
    powerwash
    return
  fi
  echo -n "Password: "
  read -s input_pass
  echo ""

  while IFS=: read -r saved_user saved_pass; do
    if [[ "$input_user" == "$saved_user" && "$input_pass" == "$saved_pass" ]]; then
      CURRENT_USER="$saved_user"
      echo "Login successful. Welcome, $CURRENT_USER!"
      sleep 1
      return
    fi
  done < "$USERS_FILE"

  echo "Invalid login. Try again."
  sleep 1
  login_screen
}

function main_menu() {
  while true; do
    draw_bg
    tput cup 2 0
    color_echo "========= NeoLT Main Menu ========="
    echo "1. NeoNote (Text Editor)"
    echo "2. NeoCalc (Calculator)"
    echo "3. NeoSys (System Info)"
    echo "4. NeoTerminal (Run Shell Commands)"
    echo "5. Settings"
    echo "6. Logout"
    echo "==================================="
    read -p "Select an option: " choice
    case $choice in
      1) neonote ;;
      2) neocalc ;;
      3) neosys ;;
      4) neoterminal ;;
      5) settings_menu ;;
      6) echo "Logging out..."; sleep 1; login_screen ;;
      *) echo "Invalid choice"; sleep 1 ;;
    esac
  done
}

function neonote() {
  read -p "Enter filename (saved to $NEOLT_DIR): " fname
  nano "$NEOLT_DIR/$fname"
}

function neocalc() {
  echo "NeoCalc - Type 'exit' to return to menu"
  while true; do
    read -p "Expression: " expr
    [[ "$expr" == "exit" ]] && break
    echo "Result: $((expr))"
  done
}

function neosys() {
  draw_bg
  color_echo "======= System Info ======="
  uname -a
  echo "User: $CURRENT_USER"
  echo "Uptime:"
  uptime
  echo "==========================="
  read -p "Press Enter to return"
}

function neoterminal() {
  echo "Welcome to NeoTerminal. Type 'exit' to return."
  while true; do
    read -p "$CURRENT_USER@neolt:~$ " cmd
    [[ "$cmd" == "exit" ]] && break
    eval "$cmd"
  done
}

function settings_menu() {
  while true; do
    draw_bg
    tput cup 2 0
    color_echo "========= Settings ========="
    echo "1. Toggle Dark Mode (Currently: $($DARK_MODE && echo ON || echo OFF))"
    echo "2. Add New User"
    echo "3. Back to Main Menu"
    echo "============================"
    read -p "Choice: " opt
    case $opt in
      1) toggle_dark ;;
      2) create_user; sleep 1 ;;
      3) return ;;
      *) echo "Invalid"; sleep 1 ;;
    esac
  done
}

function toggle_dark() {
  if $DARK_MODE; then
    echo "dark=false" > "$SETTINGS_FILE"
    DARK_MODE=false
  else
    echo "dark=true" > "$SETTINGS_FILE"
    DARK_MODE=true
  fi
  echo "Dark mode updated."
  sleep 1
}

# Entry Point
if [ ! -f "$USERS_FILE" ]; then
  setup_neolt
else
  load_settings
  login_screen
  main_menu
fi
