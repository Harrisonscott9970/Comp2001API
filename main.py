from flask import Flask, jsonify, request
import pyodbc
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)

db_config = {
    'server': 'DIST-6-505.uopnet.plymouth.ac.uk',
    'database': 'COMP2001_HScott',
    'username': 'HScott',
    'password': 'WpiG924+'
}

# Swagger configuration
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Comp2001API"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Function to create a database connection
def get_connection():
    conn_str = f"DRIVER={{ODBC Driver 18 for SQL Server}};" \
               f"SERVER={db_config['server']};" \
               f"DATABASE={db_config['database']};" \
               f"UID={db_config['username']};" \
               f"PWD={db_config['password']};" \
               f"Encrypt=no;" \
               f"TrustServerCertificate=yes"
    return pyodbc.connect(conn_str)

# Get users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, email FROM CW2.Users")
        users = [
            {'user_id': row[0], 'username': row[1], 'email': row[2]}
            for row in cursor.fetchall()
        ]
        return jsonify(users)
    except pyodbc.Error as e:
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Application error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Create a user
@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')

        if not username or not email:
            return jsonify({'error': 'Username and email are required'}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO CW2.Users (username, email) VALUES (?, ?)",
            (username, email)
        )
        conn.commit()
        return jsonify({'message': 'User created successfully'}), 201
    except pyodbc.Error as e:
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Application error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Update user information
@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE CW2.Users SET username=?, email=? WHERE user_id=?", (username, email, user_id))
        conn.commit()
        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()
        if 'cursor' in locals():
            cursor.close()

# Delete a user
@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CW2.Users WHERE user_id=?", (user_id,))
        conn.commit()
        return jsonify({'message': 'User deleted successfully'})
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()
        if 'cursor' in locals():
            cursor.close()

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        # Create connection to the database
        conn = get_connection()
        cursor = conn.cursor()

        # SQL query to fetch a user by ID
        cursor.execute("SELECT user_id, username, email FROM CW2.Users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()

        # If user found, return their details
        if user:
            return jsonify({'user_id': user[0], 'username': user[1], 'email': user[2]})
        else:
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500

    finally:
        # Close connections
        if 'conn' in locals():
            conn.close()
        if 'cursor' in locals():
            cursor.close()

# Get all trails
@app.route('/trails', methods=['GET'])
def get_trails():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trail_id, trail_name, location_name, latitude, longitude, length_miles, time_hours, difficulty, route_type, description 
            FROM CW2.Trail
        """)
        trails = [
            {
                'trail_id': row[0],
                'trail_name': row[1],
                'location_name': row[2],
                'latitude': row[3],
                'longitude': row[4],
                'length_miles': row[5],
                'time_hours': row[6],
                'difficulty': row[7],
                'route_type': row[8],
                'description': row[9]
            }
            for row in cursor.fetchall()
        ]
        return jsonify(trails)
    except pyodbc.Error as e:
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Application error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Create a trail
@app.route('/trails', methods=['POST'])
def create_trail():
    try:
        trail_data = request.get_json()

        # Map the incoming fields to the database schema
        trail_name = trail_data.get('trail_name')
        location_name = trail_data.get('trail_location')
        latitude = trail_data.get('latitude', 0.0)
        longitude = trail_data.get('longitude', 0.0)
        length_miles = trail_data.get('distance', 0)
        time_hours = trail_data.get('time_hours', 1.0)
        difficulty = trail_data.get('difficulty', 'Unknown')
        route_type = trail_data.get('route_type', 'Unknown')
        description = trail_data.get('description', 'No description')

        # Ensure required fields are provided
        if not all([trail_name, location_name, latitude, longitude, length_miles, time_hours, difficulty, route_type, description]):
            return jsonify({'error': 'All fields are required'}), 400

        # Create database connection and insert into the table
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CW2.Trail (trail_name, location_name, latitude, longitude, length_miles, time_hours, difficulty, route_type, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (trail_name, location_name, latitude, longitude, length_miles, time_hours, difficulty, route_type, description))

        # Commit and return success message
        conn.commit()
        return jsonify({'message': 'Trail created successfully'}), 201

    except pyodbc.Error as e:
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Application error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Get a specific trail by ID
@app.route('/trails/<int:trail_id>', methods=['GET'])
def get_trail(trail_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT trail_id, trail_name, location_name, latitude, longitude, length_miles, time_hours, difficulty, route_type, description FROM CW2.Trail WHERE trail_id = ?", (trail_id,))
        trail = cursor.fetchone()

        if trail:
            return jsonify({
                'trail_id': trail[0],
                'trail_name': trail[1],
                'location_name': trail[2],
                'latitude': trail[3],
                'longitude': trail[4],
                'length_miles': trail[5],
                'time_hours': trail[6],
                'difficulty': trail[7],
                'route_type': trail[8],
                'description': trail[9]
            })
        else:
            return jsonify({'error': 'Trail not found'}), 404
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()


# Update an existing trail
@app.route('/trails/<int:trail_id>', methods=['PUT'])
def update_trail(trail_id):
    try:
        trail_data = request.get_json()
        trail_name = trail_data.get('trail_name')
        location_name = trail_data.get('location_name')
        latitude = trail_data.get('latitude')
        longitude = trail_data.get('longitude')
        length_miles = trail_data.get('length_miles')
        time_hours = trail_data.get('time_hours')
        difficulty = trail_data.get('difficulty')
        route_type = trail_data.get('route_type')
        description = trail_data.get('description')

        if not all([trail_name, location_name, latitude, longitude, length_miles, time_hours, difficulty, route_type, description]):
            return jsonify({'error': 'All fields are required'}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE CW2.Trail 
            SET trail_name = ?, location_name = ?, latitude = ?, longitude = ?, length_miles = ?, time_hours = ?, difficulty = ?, route_type = ?, description = ? 
            WHERE trail_id = ?
        """, (trail_name, location_name, latitude, longitude, length_miles, time_hours, difficulty, route_type, description, trail_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Trail not found'}), 404
        
        return jsonify({'message': 'Trail updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Delete a trail
@app.route('/trails/<int:trail_id>', methods=['DELETE'])
def delete_trail(trail_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CW2.Trail WHERE trail_id = ?", (trail_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({'error': 'Trail not found'}), 404

        return jsonify({'message': 'Trail deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

@app.route('/sessions/<int:user_id>', methods=['GET'])
def get_sessions(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT session_id, trail_id, start_time, end_time 
            FROM CW2.Sessions
            WHERE user_id = ?
        """, (user_id,))
        sessions = [
            {'session_id': row[0], 'trail_id': row[1], 'start_time': row[2], 'end_time': row[3]}
            for row in cursor.fetchall()
        ]
        return jsonify(sessions)
    except pyodbc.Error as e:
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Application error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Create a session
@app.route('/sessions', methods=['POST'])
def create_session():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        trail_id = data.get('trail_id')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not all([user_id, trail_id, start_time, end_time]):
            return jsonify({'error': 'All fields are required'}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CW2.Sessions (user_id, trail_id, start_time, end_time)
            VALUES (?, ?, ?, ?)
        """, (user_id, trail_id, start_time, end_time))
        conn.commit()
        return jsonify({'message': 'Session created successfully'}), 201
    except pyodbc.Error as e:
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Application error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Delete a session
@app.route('/sessions/<int:session_id>', methods=['DELETE'])
def delete_session(session_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM CW2.Sessions WHERE session_id=?", (session_id,))
        conn.commit()
        return jsonify({'message': 'Session deleted successfully'})
    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Get all favorited trails for a user
@app.route('/favorited_trails/<int:user_id>', methods=['GET'])
def get_favorited_trails(user_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT trail_id 
            FROM CW2.Favorited_Trail
            WHERE user_id = ?
        """, (user_id,))
        trails = [{'trail_id': row[0]} for row in cursor.fetchall()]
        return jsonify(trails)
    except pyodbc.Error as e:
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Application error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Add a trail to favorites
@app.route('/favorited_trails', methods=['POST'])
def add_favorited_trail():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        trail_id = data.get('trail_id')

        if not all([user_id, trail_id]):
            return jsonify({'error': 'User ID and Trail ID are required'}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CW2.Favorited_Trail (user_id, trail_id)
            VALUES (?, ?)
        """, (user_id, trail_id))
        conn.commit()
        return jsonify({'message': 'Trail added to favorites'}), 201
    except pyodbc.Error as e:
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Application error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Remove a trail from favorites
@app.route('/favorited_trails', methods=['DELETE'])
def remove_favorited_trail():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        trail_id = data.get('trail_id')

        if not all([user_id, trail_id]):
            return jsonify({'error': 'User ID and Trail ID are required'}), 400

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM CW2.Favorited_Trail 
            WHERE user_id = ? AND trail_id = ?
        """, (user_id, trail_id))
        conn.commit()
        return jsonify({'message': 'Trail removed from favorites'})
    except pyodbc.Error as e:
        return jsonify({'error': f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({'error': f"Application error: {str(e)}"}), 500
    finally:
        if 'conn' in locals():
            conn.close()

# Entry point
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
