#!/bin/bash
#
#   Zenity Trackpoint Configuration Tool
#
#       nvz < enveezee@gmail.com >

rule_file="/etc/udev/rules.d/70-ztrackpoint.rules"

settings=(
"bind_mode"
"draghys"
"drift_time"
"ext_dev"
"inertia"
"jenks"
"mindrag"
"press_to_select"
"rate"
"reach"
"resetafter"
"resolution"
"resync_time"
"sensitivity"
"skipback"
"speed"
"thresh"
"upthresh"
"ztime"
)

title="Trackpoint Configuration Tool"

# Show Settings Form
config_form () {

	# Load current settings values into the entry array
	for setting in ${settings[*]}; do

		# Load current value for setting
		value=$(cat "$sysfs_path/$setting")

		# Save setting name to array
		entry+=("$setting")

		# Save setting value to array
		entry+=("$value")

	done

	# Create config form
	output=$(zenity --list --title "$title"\
		--text "You can edit values and select settings to write."\
		--editable --print-column=ALL --multiple --width=300 --height=680\
		--column "Setting" --column "Value" "${entry[@]}")

	# Exit if the user hit cancel
	if [[ $? == 1 ]]; then exit 0; fi

	# Parse output of list dialog into an array
	IFS="|" read -ra entry < <(echo "$output")

	# Check for selection of settings to modify
	if (( ${#entry[*]} < 2 )); then

		# Error on no selection
		no_selection

		# Restart form
		config_form

	fi

}

# No selection was made
no_selection () {

	# Output error to console
	echo "E: No selection was made!"

	# Output error to GUI
	zenity --info --title "Error" --width 300\
		--text "No selection was made!"

}

# Select trackpoint device
select_trackpoint () {

	# List available trackpoints for selection
	output=$(zenity --list --title "$title"\
		--text "Select trackpoint to configure."\
		--print-column=ALL --width=600 --height=300\
		--column "Name" --column "Sysfs Path" "${trackpoint[@]}")

	# Exit if user presses cancel
	if [[ $? == 1 ]]; then exit 0; fi

	# Parse output of list dialog into array
	IFS="|" read -ra trackpoint < <(echo "$output")

	# Check to see if user made a selection
	if (( ${#trackpoint[*]} < 2 )); then

		# Error on no selection
		no_selection

		# Restart form
		select_trackpoint

	fi

	# Set the name of the selected trackpoint
	name="${trackpoint[0]}"

	# Set the sysfs path of the selected trackpoint
	sysfs_path="${trackpoint[1]}"
}

# Detect available trackpoints
trackpoint_detect () {

	# Iterate over each mouse in /dev/input
	for mouse in /dev/input/mouse*; do

		# Get udev information of this mouse
		mouse_info=$(udevadm info -n "$mouse")

		# Check if this mouse is a INPUT_POINTINGSTICK
		if [[ "$mouse_info" =~ "POINTINGSTICK=1" ]]; then

			# Get the udev path of this mouse
			path=$(echo "$mouse_info" | grep -E "^P: " | cut -b 4-)

			# Set the sysfs path of this mouse's settings
			sysfs_path="/sys$path/device/device"

			# Set the name of this mouse
			name=$(cat "/sys$path/device/name")

			# Add the sysfs path and name of this mouse to array
			trackpoint+=("$name")
			trackpoint+=("$sysfs_path")

			# Output to console that a trackpoint was detected
			echo "$name detected at $mouse"

		fi

	done

	# See if we had found any trackpoints
	if (( ${#trackpoint[*]} > 1 )); then

		# Set count of number of detected trackpoints
		trackpoints=$((${#trackpoint[*]}/2))

		# Output to console how many trackpoints were detected
		echo "$trackpoints trackpoints detected"

		# Test to see if we found more than one trackpoint
		if (( trackpoints >= 2 )); then

			select_trackpoint

		fi

	else

		# If no trackpoints, error to console and GUI and exit.
		echo "E: No trackpoints were detected."

		zenity --info --title "Error" --width=200\
			--text "No trackpoints were detected"

		exit 1

	fi
}

# Write settings to sysfs/udev
write_settings () {

	# Generate a tempfile name
	temp_file=$(tempfile)

	# Create temp file as a bash script
	echo "#!/bin/bash" > $temp_file

	# Set excutable permissions on temp file
	chmod +x $temp_file

	# Number of settings to write
	n=$((${#entry[*]}/2))

	# Prompt to write config
	zenity --question --title "$title" --width=400 --height=100\
			--text "Write $n settings to udev rule for persistent setting?"

	# If yes was selected
	if [[ $? == 0 ]]; then

		# Then write a udev rule
		udev_rule=1

		# The idea here was to use sed or such to modify existing rules
		# however this is not implemented and the file will merely be
		# overwritten as of right now, with any settings selected.

		rules="ACTION==\"add\", SUBSYSTEM=\"input\", ATTR{name}==\"$name\""

	# If no was selected
	else

		# Then don't write udev rule
		udev_rule=0

	fi

	# Iterate over each setting in selection
	for (( c=0; c<n; c++ )); do

		# Setting to modify
		setting=${entry[$c]}

		# Value to write
		value=${entry[(($c+1))]}

		# This check verifies user did not change left col to invalid entry
		if [[ "${settings[*]}" =~ $setting ]]; then

			cat <<- EOF >> $temp_file

				# Output to console what we're modifying
				echo "Setting $setting ..."

				# Add command to modify value to a temp file
				echo "$value" > "$sysfs_path/$setting"

			EOF

			# If we are writing a rule
			if (( udev_rule == 1 )); then

				# Append the setting to the rules
				rules+=", ATTR{device/$setting}=\"$value\""

			fi

		fi

	done

	# if we wrote a rule, then write it to file and reload the rules
	if (( udev_rule == 1 )); then

		# Write heredoc to a temp file
		cat <<- EOF >> $temp_file

			# Output to console that we're writing udev rules
			echo "Writing udev rules ..."

			# Create the rules file
			echo "$rules" > "$rule_file"

			# Reload the udev rules
			udevadm control --reload-rules

		EOF

	fi

	# Use polkit to execute the temp file as root to apply changes
	pkexec $temp_file

	# Cleanup temp file
	rm $temp_file

}

# Detect trackpoints
trackpoint_detect

# Display config UI
config_form

# Write settings to sysfs/udev
write_settings
