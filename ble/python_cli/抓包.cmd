@REM REM python sniff_receiver.py -s COM11 -m EA:8F:D9:27:CE:B3 -o data2.pcap
@REM python sniff_receiver.py -s COM11 -m B3:55:44:44:55:B3 -o data3.pcap
REM python sniff_receiver.py -s COM11 -a -o data3.pcap
python sniff_receiver.py -s COM21 -o data4.pcap -m a4:9f:89:af:b6:57
pause