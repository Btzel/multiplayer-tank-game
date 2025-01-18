# MULTIPLAYER TANK GAME

```
Burak TÜZEL
Talha Alper ASAV
Supervisor:
Ahmet Çağdaş SEÇKİN
June 2024
```

**Declaration**
```
I declare that scientific ethics and academic rules are meticulously complied with in
the design, preparation, execution, research, and analysis of this thesis, and the
findings, data, and materials that are not directly the primary product of this study are
cited in accordance with scientific ethics.
```

**The Goal of The Project**
```
The fundamental aim of the project is making multiplayer tank game and autonomous
game-playing agent that play the game in the place of a human using the data
obtained by the Host. The development process proceeds as follows; Finding assets,
creating project, creating multiplayer infrastructure, collecting data from players and
training AI-based players within collected data. The result of the project is including
single player tank game that has progressive game design against AI-based enemies
and, multiplayer tank game that has competitive environment that online players can
enjoy playing with their friends connected to the same internet connection.
```
**Keywords**

```
Multiplayer, Tank, AI, Training, Competitive
```

**1. INTRODUCTION**
```
The aim of this manual is to explain how to make multiplayer tank game and how to train
AI-based players on Unity Engine. The progress is going to be shown in the next sections in
the manual.
```
```
## 2. FINDING REQUIRED ASSETS
The assets can be explained as graphical textures, sounds, objects and more.
```
```
## 3. REQUIRED SOFTWARES
Software used in this project; Unity Engine, Visual Studio 2022, Python Development IDE.
```
```
## 3.1 Installing Unity Engine and Unity Editor
Unity Engine is free to use game engine can be downloaded from their website [2]. After
installing Unity Hub, the Unity Editor can be downloaded as shown below.
```
```
## 3.2 Installing Visual Studio
Visual Studio can be downloaded from their website [3].After downloading Visual Studio
Installer, the Game Develoment with Unity package should be installed as shown below.
```
```
## 4. CREATING UNITY PROJECT
New project can be created from Unity Hub
```
```
## 5. NETCODE FOR GAMEOBJECTS
In a multiplayer game, players act as clients connecting to a server, which is typically hosted
by the game company. Players send data to the server, which processes it and communicates
back to the clients. For example, if a player fires a weapon, the server handles the logic and
notifies other clients about the resulting actions, such as the spawning of a projectile.
``

_Self-Hosted Model_

In the self-hosted model, a player’s machine functions as both the client and the server,
running the game and server logic. Other players connect to this host player. This model
offers simplicity and cost efficiency since there is no need for dedicated server hosting.
However, it has significant downsides:

1. Lag: The host's internet quality directly impacts all players.
2. Host Advantage: The host player experiences zero ping, providing an unfair advantage.
3. Cheating Risks: The host, having access to the server code, can potentially manipulate the
    game.

_Dedicated Server Model_

Dedicated servers involve a non-player entity, located in a server farm with high-speed
internet and optimized hardware, running the server code. Clients only connect to this server.
The benefits include:

1. Security: Players do not expose their network to others.
2. Fairness: All players connect to the server, eliminating host advantages.
3. Performance: Servers focus solely on game logic without the overhead of running game
    clients.

However, dedicated servers also have downsides:

1. Cost: Hosting dedicated servers incurs additional expenses. Although services like Unity’s
    UGS offer free tiers for testing, scaling up requires payment.
2. Complexity: Implementing dedicated servers is more complex, involving matchmaking and
    server management.

The project will cover only self hosted model.
```

```
## 6. BUILDING THE FOUNDATIONS OF THE GAME

Required packages

- Netcode for Gameobjects
- com.unity.services.multiplay
- Cinemachine
- Input System
```
```

## 6.1 Core Gameplay..........................................................................................................

- **_Assets_**
The assets to be used in the game were found on the internet and imported into the Unity
Editor. Afterwards, the player's prefab was created using these assets.
- **_Inputs_**
Unity's input system was used to control mechanics such as moving and shooting


- **_NetworkManager and NetworkTransform_**
The NetworkManager component in Unity's Netcode framework for GameObjects is crucial
for managing various aspects of multiplayer networking. Developers can ensure a stable and
functional multiplayer environment by adhering to the guidelines and effectively managing
network connections, settings, and activities using available methods and features.In this
project, Network Manager was used to manage connections in the game

The NetworkTransform component in Unity's Netcode for GameObjects framework allows
developers to handle transform synchronization effectively. By configuring the component
properly and using the provided techniques for dealing with network conditions, developers
can ensure a smoother and more efficient multiplayer experience. Client Network Transform
was used to handle objects transform syncronization in the game environment. Network
Transform is Server-Authoritativc and Client Network Transform Client-Authoritative. So,
using Client Network Transform gives the client the control over the position, rotation, and
scale of the object it owns.


- **_Player Movement_**
Player movement achieved by rotating the tank hull in the z-axis and moving in the direction
the hull is facing or vice versa.
- **_Player Aiming_**
Player Aiming achieved by taking the position of mouse cursor, and setting turret’s up
vector to point at the cursor.


- **_Firing Projectiles_**
Firing Projectiles when fire was triggered pressing Mouse0 button or Space key achieved by
creating two projectile prefabs. One is client side projectile and the other is server side
projectile. Client side projectile is just a visualization of the projectile, so it has no effect
such as damaging to enemies. Server side projectile is the real projectile which is going to do
the damaging. The reason of this approach is to prevent the advantage or disadvantage
players have due to their connection status.

ServerRpc: Used for client-to-server communication for server-authoritative actions.
ClientRpc: Used for server-to-client communication to update clients about change.

The code below basicaly handles firing client side and server side projectile.


- **_Health_**
The player's health component was created to perform actions such as taking damage and
restoring health for the player. Afterwards, the health of a player displayed on the top of
players.


- **_Handling Damage_**
The player's health was when the player collided with a projectile
- **_Coin and Coin Wallet_**
The coin prefab and coin wallet were added to create a game mechanism where players can
refill their health and shoot using coins.


- **_Coin Spawner_**
The coin spawner was created to handle certain amount of coin spawn inside a map borders.


- **_Map Design_**
Map was created using the assets installed from the internet.
```
```


## 6.2 Connection

- **_Main Menu_**
The main menu scene and UI was created to make players can connect over the internet and
create a lobby for other players to join.
- **_Application Controller_**
The Application Controller was created to check if the player is dedicated server, client or host. It
sends a server, client or host code depending on the players status. Once this process is completed, it
will spawn Server Singleton or Client and Host Singleton. Each of those Singletons have their own
manager scripts to provide managing interaction with Unity Gaming Services. Server Manager and
Client Manager Singleton has their own Network Server and Network Client logic which is the main
game logic.
- ApplicationController.cs


- Server, Client and Host Singletons


- Server Game Manager


- Host Game Manager


- Client Game Manager


- Network Server


- Network Client


- **_Authentication_**
The authentication method was used to achieve adding authentication to the game. When the
player hits "Connect" they will be taken to the first scene, which will attempt to authenticate
them. If successful, they are then sent to the main menu and granted access to game services.

```
```
▪ Setting Up Relay Service

Relay Service allows players to connect to a game over the Internet without needing to port
forward their routers, so Relay is added to provide this feature in Manager and Singleton
scripts.

▪ **_Lobbies_**
Unity Gaming Service provides lobby service to create and manage multiplayer game
lobbies. Players can browse a list of active lobbies, join, and then connect to the game’s
relay connection. Lobbies feature was adapted into project to give the host an ability create a
lobby and give the host an ability to able to see the active lobbies and join them in the
HostGameManager, and Lobby scripts


▪ **_Player Name Selection_**
A name selection feature was added to the project to allow players can choose their names
before connecting to the server. Player’s name is displayed on their tanks

▪ **_Connection Approval_**
Connection Approval is a feature in Netcode for GameObjects that allows the server to
approve or reject client connections based on custom logic. This can be useful for various
purposes, such as authenticating users, managing player data, and preventing unauthorized
access. This feature was added in the NetworkServer, NetworkClient, ClientGameManager
and HostGameManager scripts given above
```
```

## 6.3 Gameplay Additions................................................................................................

▪ **_Respawning_**
Respawning algorithm was applied to respawn when the player is died.

▪ **_Healing Zone_**
Healing Zones were added to the game to achieve players refill their heath
```
```
## 7. Multiplayer Tank Game Autonomous Agent

▪ **_Overview_**
Project focuses on developing an autonomous game-playing agent that can navigate, make
decisions, and interact within a game environment. This agent utilizes various algorithms
and techniques including pathfinding, decision-making, and object detection to achieve its
goals.
o **_Key Steps_**

- Data collection: The GatherDataset.py script was created to capture
    game frames.
- **_Data Labeling:_** Labeling process was made in Roboflow labeling
    website.
- **_Model Training:_** After labeling process, yolov8 instance created from
    Roboflow website and trained the object detection model
- **_Integration:_** Matrix generation was done by Matrix.py which is
    generating a matrix representation of the game map, along with a
    distance map to facilitate pathfinding. Pathfinding was done by Astar.py
    using bidirectional A* algorithm to create a path between 2 given points
    on the map matrix. Decision Making was done by DecisionMaker.py to
    choose actions based on the current game environment such as
    teammate number, enemy number, players health etc. The post process
    of the pathfinding and pathing logic was done by MapPathfinder.py by
    smoothing the path, finding nearest point, checking the points that
    player can go etc. Lastly, object detection and implementation of actions
    was done by YoloInference.py by capturing the game frames and
    detecting objects, reaching to the actions based on the environmental
    state, and implementing the action which is decided to.

▪ **_Approach_**
The project combines computer vision, pathfinding algorithms, and game state analysis to
create a sophisticated autonomous agent capable of real-time decision-making and
interaction within a game environment. This approach ensures effective solution for
developing AI agents for complex game scenarios.
```

```
▪ Components
o Matrix.py Key Functions
```
- create_distance_map(matrix): Initializes a distance map from obstacles by
    using a Breadth-First Search (BFS) algorithm to compute distances.
- create_matrix(image_rgb): Converts an RGB image to a matrix with specific
    values representing different terrains (walkable areas, obstacles, healing
    zones).



**_Matrix.py Key Functions Representation_**
```

```
o Astar.py Key Functions
```
- bidirectional_astar(matrix, start, goal, obstacle_distance_map): Utilizing two
    simultaneous A* searches from the start and goal nodes to meet in the
    middle, reducing the search space and improving efficiency.
- heuristic(a, b, obstacle_distance_map): Computes the heuristic cost to guide
    the A* search algorithm.
**_Astar.py Key Functions Representation_**



```
o DecisionMaker.py Key Functions
```
- make_decision(previous_state, player_health, player_gold,
    enemy_count, teammate_count, coins_nearby): Generates a decision
    based on various game parameters.
**_DecisionMaker.py Key Functions Representation_**


o **_MapPathfinder.py Key Functions_**

- find_path(decision, map_image_copy, matrix, distance_map): Finds
    the appropriate path based on the agent's decision.
- visualise_path(smoothed_path, map_image_copy, player_position):
    Visualizes the path on the game map.
- draw_path(image, path): Draws the path on the game map image.
- create_goal_point(smoothed_path, common_path): Writes the goal
    point of the path to a file.
- create_movement_vector(smoothed_path, common_path): Writes
    the movement vector to a file.


**_MapPathfinder.py Key Functions Representation_**



```
o YoloInference.py Key Functions
```
- non_max_suppression(...): Applies Non-Maximum Suppression to
    filter overlapping detections.
- process_handler(results, names, fps, frame): Processes detection
    results and updates the agent's state.
- action_handler(...): Executes actions based on the determined
    decision.
- capture_game_window(): Captures the current game window for
    processing.
- read_movement_vector(): Reads the movement vector from a file.
**_YoloInference.py Key Functions Representation_**





**_Workflow_**

1. Initialization: The game map is loaded and converted into a matrix and a distance map.
    A YOLO model is initialized for object detection.
2. Game State Reading: The script reads the game state including player position, health,
    resources, and enemy positions.
3. Decision Making: Based on the current state, a decision is made using predefined rules in the
    DecisionMaker.py script.
4. Pathfinding: A path is calculated using the A* algorithm if movement is required based on
    the decision. The path is smoothed and visualized.
5. Action Execution: The agent executes actions such as moving towards a goal, collecting
    items, evading enemies, or engaging in combat.
6. Visualization and Logging: The current state, decisions, and paths are visualized and logged
    for debugging and analysis.


```


**References**
```
[1] YumingRong, Github, (2019). Accesed: Dec. 22, 2023. [Online]. Available:
https://github.com/YumingRong/90-Tank/tree/TankAI/Assets

[2] Unity, Unity 2022.3.11f1, (2022). Accessed: Dec. 22, 2023. [Online].
Available: https://unity.com

[3] Microsoft, .Net Conf 2023, (2023). Accessed: Dec. 22, 2023. [Online].
Available: https://visualstudio.microsoft.com/tr/

[4] Unity Multiplayer Networking, Netcode for GameObjects 1.6.0, (2023).
Accessed: Dec. 22, 2023. [Online]. Available: https://docs-
multiplayer.unity3d.com/netcode/current/components/networkmanager/

[5] Unity Multiplayer Networking, Netcode for GameObjects 1.6.0, (2023).
Accessed: Dec. 22, 2023. [Online]. Available: https://docs-
multiplayer.unity3d.com/netcode/current/basics/networkobject/

[6] Unity Multiplayer Networking, Netcode for GameObjects 1.6.0, (2023).
Accessed: Dec. 22, 2023. [Online]. Available: https://docs-
multiplayer.unity3d.com/netcode/current/components/networktransform/

[7] Unity Multiplayer Networking, Netcode for GameObjects 1.6.0, (2023).
Accessed: Dec. 22, 2023. [Online]. Available: https://docs-
multiplayer.unity3d.com/netcode/current/advanced-topics/message-
system/serverrpc/

[8] Unity Multiplayer Networking, Netcode for GameObjects 1.6.0, (2023).
Accessed: Dec. 22, 2023. [Online]. Available: https://docs-
multiplayer.unity3d.com/netcode/current/advanced-topics/message-
system/clientrpc/

[9] Carl Boisvert Dev, Unity Netcode For Gameobject – Client Prediction). (Nov.
27, 2022). Accessed: Sept 13, 2023. [Online Video]. Available:
https://www.youtube.com/watch?v=leL6MdkJEaE

[10] Code Monkey, Field of View Effect in Unity (Line of Sight, View Cone). (Oct.
13, 2019). Accessed: Nov. 18, 2023. [Online Video]. Available:
https://www.youtube.com/watch?v=CSeUMTaNFYk

[11] Code Monkey, Complete Unity Multiplayer Tutorial (Netcode for Game
Objects). (Sept. 26, 2022). Accessed: Sept. 3, 2023. [Online Video]. Available:
https://www.youtube.com/watch?v=3yuBOB3VrCk


