def fill_data(data):
    length = len(data['coordenadas'])
    def fill_arr(arr):
        res = []
        last = None
        for i in range(length):
            if i < len(arr) and arr[i] is not None:
                last = arr[i]
                res.append(arr[i])
            else:
                res.append(last)
        return res
    return {
        "coordenadas": data["coordenadas"],
        "hrs": fill_arr(data["hrs"]),
        "altitudes": fill_arr(data["altitudes"]),
        "distancias": fill_arr(data["distancias"]),
        "times": fill_arr(data["times"]),
        "cadencias": fill_arr(data["cadencias"]),

    }