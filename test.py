import av

if __name__ == '__main__':

    # Откроем ресурс на чтение
    input_resource = av.open(
        'test_2.sdp',  #'rtmp://src_stream:1935/play'
        options=dict({'protocol_whitelist': 'file,udp,rtp'})
    )

    # Откроем ресурс на запись.
    output_resource = av.open(
        'rtmp://gpu3.view.me/live/test890',
        mode='w',
        format='flv',
        options=dict({'protocol_whitelist': 'file,udp,tcp,rtmp,udp,rtp'})
    )
    # Список потоков входного ресурса: видео и аудио
    input_streams = list()
    # Список потоков выходного ресурса: видео и аудио
    output_streams = list()
    # Для входного и выходного ресурсов возьмём поток видео.
    for stream in input_resource.streams:
        if stream.type == 'video':
            input_streams += [stream]
            # Создадим видео-поток для выходного ресурса. Кодек `h264`.
            output_streams += [output_resource.add_stream('h264')]
            break
    # Для входного и выходного ресурсов возьмём поток аудио.
    for stream in input_resource.streams:
        if stream.type == 'audio':
            input_streams += [stream]
            # Создадим аудио-поток для выходного ресурса. Кодек `aac`.
            output_streams += [output_resource.add_stream('aac')]
            break
    # В этом списке будем хранить пакеты выходного потока.
    output_packets = list()
    # Применим «инверсное мультиплексирование». Получим пакеты из потока.
    for packet in input_resource.demux(input_streams):
        # Получим все кадры пакета.
        for frame in packet.decode():
            # Сбросим PTS для самостоятельного вычислении при кодировании.
            frame.pts = None
            # Закодируем соответствующие кадры для выходных потоков.
            for stream in output_streams:
                if packet.stream.type == stream.type:
                    output_packets += [stream.encode(frame)]
    # Сбросим буфферы кодировщика. ??? Нужно ли ???
    for stream in output_streams:
        output_packets += [stream.encode(None)]
    # Для каждого пакета применим «прямое мультиплексирование».
    for packet in output_packets:
        if packet: output_resource.mux(packet)
    output_resource.close()