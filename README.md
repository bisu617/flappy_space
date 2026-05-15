# Flappy Space: Enhanced Edition

A professional Python (Pygame) version of the classic Flappy Space game, featuring difficulty levels and a global leaderboard.

## Features
- **4 Difficulty Levels**: Easy, Intermediate, Hard, Impossible.
- **Global Leaderboard**: Compete with other players worldwide.
- **Modern UI**: Polished menus and game-over screens.
- **Web Ready**: Can be bundled for the web using `pygbag`.

## How to setup the Global Leaderboard
1. Create a free account at [Supabase](https://supabase.com).
2. Create a new project.
3. In the SQL Editor, run the following script to create the leaderboard table:
   ```sql
   create table leaderboard (
     id uuid default gen_random_uuid() primary key,
     created_at timestamptz default now(),
     username text not null,
     score int not null,
     level text not null
   );
   
   -- Enable public access (for testing, you should add proper security later)
   alter table leaderboard enable row level security;
   create policy "Enable access to all users" on leaderboard for all using (true);
   ```
4. Go to **Project Settings -> API** and copy your `Project URL` and `anon public` Key.
5. Paste them into `database.py`:
   ```python
   SUPABASE_URL = "your-project-url"
   SUPABASE_KEY = "your-anon-key"
   ```

## Controls
- **SPACE**: Jump / Start Game / Restart
- **1-4**: Select Difficulty (in Menu)
- **L**: View Leaderboard (in Menu)
- **M**: Return to Menu (in Game Over / Leaderboard)
- **S**: Submit Score (in Game Over)

## Running the game
```bash
pip install pygame
python main.py
```
