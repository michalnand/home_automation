while true
do
    cd $HOME/projects/home_automation/tests/
    python3 i2c_test.py
    sleep 5
    cd 
done
